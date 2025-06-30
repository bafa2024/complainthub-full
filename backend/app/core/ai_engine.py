# backend/app/core/ai_engine.py

import openai
import os
from ..config import settings
from ..schemas import TicketCategoryEnum, TicketUrgencyEnum
import logging
import json
import traceback
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        try:
            # Try to get OpenAI API key from settings method
            self.openai_api_key = settings.get_openai_api_key()
            self.has_openai_key = bool(self.openai_api_key and self.openai_api_key.strip())
            
            if self.has_openai_key:
                openai.api_key = self.openai_api_key
                logger.info("OpenAI API key configured successfully")
            else:
                logger.warning("OpenAI API key not found. AI features will use fallback responses.")
            
            self.model = "gpt-3.5-turbo"  # Using a modern, cost-effective chat model
            
        except Exception as e:
            logger.error(f"Error initializing AIEngine: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.has_openai_key = False
            self.model = "gpt-3.5-turbo"

    def _get_chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Helper function to get a chat completion from OpenAI."""
        try:
            if not self.has_openai_key:
                logger.info("OpenAI not available, returning fallback response")
                return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,  # Low temperature for predictable, factual responses
            )
            return response.choices[0].message.content.strip()
            
        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"

    def classify_intent_and_extract_details(self, text: str) -> dict:
        """
        Analyzes the user's text to classify its intent, urgency, sentiment,
        and extracts key details for ticket creation.
        """
        try:
            if not self.has_openai_key:
                logger.info("OpenAI not available, returning fallback analysis")
                return {
                    "category": TicketCategoryEnum.complaint.value,
                    "urgency": TicketUrgencyEnum.medium.value,
                    "abuse_flag": False,
                    "title": "Complaint submitted via chat",
                    "extracted_details": text,
                }
            
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

            response_json_str = self._get_chat_completion(system_prompt, user_prompt)
            
            # Clean the response to ensure it's valid JSON
            # Sometimes the model might wrap the JSON in markdown backticks
            if response_json_str.startswith("```json"):
                response_json_str = response_json_str[7:-4].strip()
            elif response_json_str.startswith("```"):
                response_json_str = response_json_str[3:-3].strip()

            parsed_response = json.loads(response_json_str)
            
            # Validate enums to prevent errors
            if parsed_response.get("category") not in [e.value for e in TicketCategoryEnum]:
                logger.warning(f"Invalid category '{parsed_response.get('category')}', using fallback")
                parsed_response["category"] = TicketCategoryEnum.complaint.value
            
            if parsed_response.get("urgency") not in [e.value for e in TicketUrgencyEnum]:
                logger.warning(f"Invalid urgency '{parsed_response.get('urgency')}', using fallback")
                parsed_response["urgency"] = TicketUrgencyEnum.medium.value

            return parsed_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {response_json_str}")
            return {
                "category": TicketCategoryEnum.complaint.value,
                "urgency": TicketUrgencyEnum.medium.value,
                "abuse_flag": False,
                "title": "Could not determine title",
                "extracted_details": text,
            }
        except KeyError as e:
            logger.error(f"Missing key in AI response: {e}")
            return {
                "category": TicketCategoryEnum.complaint.value,
                "urgency": TicketUrgencyEnum.medium.value,
                "abuse_flag": False,
                "title": "Could not determine title",
                "extracted_details": text,
            }
        except Exception as e:
            logger.error(f"An unexpected error occurred in classify_intent_and_extract_details: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "category": TicketCategoryEnum.complaint.value,
                "urgency": TicketUrgencyEnum.medium.value,
                "abuse_flag": False,
                "title": "Error occurred during analysis",
                "extracted_details": text,
            }

    def generate_follow_up_question(self, conversation_history: list) -> str:
        """
        Based on the conversation history, generate a relevant follow-up question
        to gather any missing information needed for a complete ticket.
        """
        try:
            if not self.has_openai_key:
                logger.info("OpenAI not available, returning fallback question")
                fallback_questions = [
                    "Could you please provide the order number for your purchase?",
                    "What is the email address associated with your account?",
                    "Can you tell me the date and time the incident occurred?",
                    "Could you provide more details about what happened?",
                    "What would you like us to do to resolve this issue?"
                ]
                import random
                return random.choice(fallback_questions)
            
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
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Could you please provide more details about your issue?"