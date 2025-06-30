# backend/app/core/conversation_manager.py

import logging
from .ai_engine import AIEngine
from app import crud, schemas
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# In-memory store for conversations. In a production environment,
# this should be replaced with a persistent store like Redis.
CONVERSATION_STORE = {}
MAX_DIALOG_TURNS = 4 # Initial user message + 3 follow-up questions

class ConversationManager:
    def __init__(self, db: Session, ai_engine: AIEngine):
        self.db = db
        self.ai_engine = ai_engine

    def process_message(self, session_id: str, user_message: str, brand_id: int, channel: str):
        """
        Main entry point to process an incoming user message.
        """
        if session_id not in CONVERSATION_STORE:
            # New conversation
            CONVERSATION_STORE[session_id] = {
                "history": [],
                "state": "started",
                "turn_count": 0
            }

        # Append user message to history
        CONVERSATION_STORE[session_id]["history"].append({"role": "user", "content": user_message})
        CONVERSATION_STORE[session_id]["turn_count"] += 1

        conversation = CONVERSATION_STORE[session_id]

        if conversation["turn_count"] >= MAX_DIALOG_TURNS:
            # Max turns reached, create ticket with available info
            bot_response = "Thank you. I have collected all the information I can. A support ticket is being created, and an agent will review it shortly."
            self._create_ticket_from_conversation(session_id, brand_id, channel)
        else:
            # Ask a follow-up question
            follow_up_question = self.ai_engine.generate_follow_up_question(conversation["history"])
            bot_response = follow_up_question
            CONVERSATION_STORE[session_id]["history"].append({"role": "assistant", "content": bot_response})
        
        return bot_response

    def _create_ticket_from_conversation(self, session_id: str, brand_id: int, channel: str):
        """
        Creates a ticket in the database based on the conversation history.
        """
        conversation = CONVERSATION_STORE.get(session_id)
        if not conversation:
            return

        full_conversation_text = " ".join([turn["content"] for turn in conversation["history"] if turn["role"] == "user"])

        # Use AI to analyze the full conversation
        analysis = self.ai_engine.classify_intent_and_extract_details(full_conversation_text)
        
        # Find or create user based on session_id (e.g., phone number)
        # For this example, we'll assume a dummy user. This needs real implementation.
        user = crud.get_user_by_email(self.db, email="default-user@example.com")
        if not user:
            user_in = schemas.UserCreate(email="default-user@example.com", password="dummy_password", full_name="Default User")
            user = crud.create_user(self.db, user_in)
        
        ticket_in = schemas.TicketCreate(
            title=analysis.get("title", "Ticket created by bot"),
            description=full_conversation_text,
            brand_id=brand_id,
            channel=channel
        )

        # Create the ticket
        db_ticket = crud.create_ticket(self.db, ticket=ticket_in, owner_id=user.id)
        
        # Update ticket with AI analysis results
        ticket_update = schemas.TicketUpdate(
            category=analysis.get("category"),
            urgency=analysis.get("urgency"),
            abuse_level_flag=analysis.get("abuse_flag")
        )
        crud.update_ticket(self.db, ticket_id=db_ticket.id, ticket_update=ticket_update)

        logger.info(f"Ticket {db_ticket.id} created for session {session_id}")

        # Clean up conversation from store
        del CONVERSATION_STORE[session_id]