# backend/app/core/ai_engine.py

import openai
from app.config import settings
from app.schemas import TicketCategoryEnum, TicketUrgencyEnum
import logging
import json

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo" # Using a modern, cost-effective chat model

    def _get_chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Helper function to get a chat completion from OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0, # Low temperature for predictable, factual responses
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def classify_intent_and_extract_details(self, text: str) -> dict:
        """
        Analyzes the user's text to classify its intent, urgency, sentiment,
        and extracts key details for ticket creation.
        """
        system_prompt = f"""
            You are an expert AI assistant for a complaint management system.
            Your task is to analyze the user's message and extract key information in a structured JSON format.

            The JSON output must contain the following fields:
            - "category": Classify the user's intent into one of these categories: {', '.join([e.value for e in TicketCategoryEnum])}.
            - "urgency": Assess the urgency from the user's language. Classify into one of: {', '.join([e.value for e in TicketUrgencyEnum])}.
            - "abuse_flag": Set to true if the user's language is abusive, toxic, or contains profanity, otherwise false.
            - "title": A concise, 5-10 word summary of the user's issue.
            - "extracted_details": Any specific details mentioned like product names, order numbers, dates, or locations.

            Analyze the user's text and provide only the JSON object as a response.
        """
        
        user_prompt = f"Analyze the following text: '{text}'"

        try:
            response_json_str = self._get_chat_completion(system_prompt, user_prompt)
            # Clean the response to ensure it's valid JSON
            # Sometimes the model might wrap the JSON in markdown backticks
            if response_json_str.startswith("```json"):
                response_json_str = response_json_str[7:-4].strip()

            parsed_response = json.loads(response_json_str)
            
            # Validate enums to prevent errors
            if parsed_response.get("category") not in [e.value for e in TicketCategoryEnum]:
                parsed_response["category"] = TicketCategoryEnum.complaint.value
            
            if parsed_response.get("urgency") not in [e.value for e in TicketUrgencyEnum]:
                parsed_response["urgency"] = TicketUrgencyEnum.medium.value

            return parsed_response

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}. Response: {response_json_str}")
            # Fallback in case of parsing failure
            return {
                "category": TicketCategoryEnum.complaint.value,
                "urgency": TicketUrgencyEnum.medium.value,
                "abuse_flag": False,
                "title": "Could not determine title",
                "extracted_details": text,
            }
        except Exception as e:
            logger.error(f"An unexpected error occurred in classify_intent_and_extract_details: {e}")
            raise

    def generate_follow_up_question(self, conversation_history: list) -> str:
        """
        Based on the conversation history, generate a relevant follow-up question
        to gather any missing information needed for a complete ticket.
        """
        system_prompt = """
            You are a conversational AI for a customer support bot.
            Your goal is to gather enough information to file a complete complaint ticket.
            The user has provided an initial statement. Based on the conversation so far,
            ask a single, clear, and concise question to get the remaining necessary details.
            
            Do not greet the user. Just ask the question.
            Example questions:
            - "Could you please provide the order number for your purchase?"
            - "What is the email address associated with your account?"
            - "Can you tell me the date and time the incident occurred?"
        """
        
        # We only need the user's messages to formulate the next question
        user_conversation = "\n".join([f"User: {turn['content']}" for turn in conversation_history if turn['role'] == 'user'])
        
        user_prompt = f"Here is the conversation so far:\n{user_conversation}\n\nWhat is the best follow-up question to ask?"

        return self._get_chat_completion(system_prompt, user_prompt)