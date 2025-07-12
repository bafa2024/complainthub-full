# backend/app/core/conversation_manager.py

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .ai_engine import AIEngine
from app.models import (
    ConversationSession, ConversationTurn, SessionContext, 
    FollowUpTemplate, Ticket, User, Brand, AILearningData
)
from app import crud, schemas

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, db: Session, ai_engine: AIEngine):
        self.db = db
        self.ai_engine = ai_engine
        self.max_context_turns = 10  # Number of recent turns to include in context

    def process_message(self, session_id: str, user_message: str, brand_id: int, 
                       channel: str, language: str = "en", user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Main entry point to process an incoming user message with contextual follow-ups.
        """
        try:
            # Get or create conversation session
            session = self._get_or_create_session(session_id, brand_id, user_id, channel, language)
            
            # Add user message to conversation history
            user_turn = self._add_conversation_turn(
                session.id, "user", user_message, turn_number=self._get_next_turn_number(session.id)
            )
            
            # Analyze the message with context
            analysis = self._analyze_message_with_context(user_message, session)
            
            # Update session context with new information
            self._update_session_context(session.id, analysis, user_turn.id)
            
            # Generate contextual response
            response = self._generate_contextual_response(session, user_message, analysis)
            
            # Add bot response to conversation history
            bot_turn = self._add_conversation_turn(
                session.id, "assistant", response["message"], 
                turn_number=self._get_next_turn_number(session.id),
                ai_analysis=analysis
            )
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            self.db.commit()
            
            # Store for learning
            self._store_for_learning(session, user_message, analysis, response)
            
            return {
                "session_id": session_id,
                "message": response["message"],
                "analysis": analysis,
                "follow_up_required": response.get("follow_up_required", False),
                "follow_up_type": response.get("follow_up_type"),
                "context_summary": response.get("context_summary"),
                "turn_number": bot_turn.turn_number
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._get_fallback_response(language)

    def _get_or_create_session(self, session_id: str, brand_id: int, user_id: Optional[int], 
                              channel: str, language: str) -> ConversationSession:
        """Get existing session or create new one"""
        try:
            # Try to find existing session
            session = self.db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id,
                ConversationSession.brand_id == brand_id
            ).first()
            
            if session:
                # Check if session is still active (not abandoned)
                if session.status == "abandoned":
                    # Reactivate session
                    session.status = "active"
                    session.last_activity = datetime.utcnow()
                    self.db.commit()
                return session
            
            # Create new session
            session = ConversationSession(
                session_id=session_id,
                brand_id=brand_id,
                user_id=user_id,
                channel=channel,
                language=language,
                status="active"
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Created new conversation session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error getting/creating session: {e}")
            raise

    def _add_conversation_turn(self, session_id: int, role: str, content: str, 
                              turn_number: int, ai_analysis: Optional[Dict] = None) -> ConversationTurn:
        """Add a conversation turn to the database"""
        try:
            turn = ConversationTurn(
                session_id=session_id,
                turn_number=turn_number,
                role=role,
                content=content,
                ai_analysis=ai_analysis
            )
            
            if ai_analysis:
                turn.intent_detected = ai_analysis.get("category")
                turn.sentiment_score = ai_analysis.get("sentiment_score")
                turn.urgency_level = ai_analysis.get("urgency")
                turn.follow_up_required = ai_analysis.get("follow_up_required", False)
                turn.follow_up_type = ai_analysis.get("follow_up_type")
            
            self.db.add(turn)
            self.db.commit()
            self.db.refresh(turn)
            
            return turn
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {e}")
            raise

    def _get_next_turn_number(self, session_id: int) -> int:
        """Get the next turn number for a session"""
        try:
            last_turn = self.db.query(ConversationTurn).filter(
                ConversationTurn.session_id == session_id
            ).order_by(desc(ConversationTurn.turn_number)).first()
            
            return (last_turn.turn_number + 1) if last_turn else 1
            
        except Exception as e:
            logger.error(f"Error getting next turn number: {e}")
            return 1

    def _analyze_message_with_context(self, message: str, session: ConversationSession) -> Dict[str, Any]:
        """Analyze message with conversation context"""
        try:
            # Get recent conversation context
            recent_turns = self._get_recent_conversation_turns(session.id)
            session_context = self._get_session_context(session.id)
            
            # Build context string
            context_string = self._build_context_string(recent_turns, session_context)
            
            # Analyze with AI engine using context
            analysis = self.ai_engine.analyze_text_with_context(
                text=message,
                context=context_string,
                brand_id=session.brand_id
            )
            
            # Enhance analysis with session-specific information
            analysis = self._enhance_analysis_with_session_data(analysis, session, recent_turns)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing message with context: {e}")
            # Fallback to basic analysis
            return self.ai_engine.analyze_text(message)

    def _get_recent_conversation_turns(self, session_id: int, limit: int = None) -> List[ConversationTurn]:
        """Get recent conversation turns for context"""
        try:
            limit = limit or self.max_context_turns
            turns = self.db.query(ConversationTurn).filter(
                ConversationTurn.session_id == session_id
            ).order_by(desc(ConversationTurn.turn_number)).limit(limit).all()
            
            return list(reversed(turns))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error getting recent conversation turns: {e}")
            return []

    def _get_session_context(self, session_id: int) -> Dict[str, Any]:
        """Get session context information"""
        try:
            contexts = self.db.query(SessionContext).filter(
                SessionContext.session_id == session_id,
                SessionContext.is_active == True
            ).all()
            
            context_dict = {}
            for context in contexts:
                if context.context_type not in context_dict:
                    context_dict[context.context_type] = {}
                context_dict[context.context_type][context.context_key] = context.context_value
            
            return context_dict
            
        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return {}

    def _build_context_string(self, turns: List[ConversationTurn], context: Dict[str, Any]) -> str:
        """Build context string from conversation turns and session context"""
        try:
            context_parts = []
            
            # Add conversation history
            if turns:
                conversation_history = []
                for turn in turns[-5:]:  # Last 5 turns
                    role = "User" if turn.role == "user" else "Assistant"
                    conversation_history.append(f"{role}: {turn.content}")
                
                context_parts.append("Recent conversation:\n" + "\n".join(conversation_history))
            
            # Add session context
            if context.get("issue_details"):
                issue_details = context["issue_details"]
                if "issue_type" in issue_details:
                    context_parts.append(f"Issue: {issue_details['issue_type']}")
                if "order_number" in issue_details:
                    context_parts.append(f"Order: {issue_details['order_number']}")
                if "product_name" in issue_details:
                    context_parts.append(f"Product: {issue_details['product_name']}")
            
            if context.get("user_preferences"):
                user_prefs = context["user_preferences"]
                if "preferred_language" in user_prefs:
                    context_parts.append(f"User prefers: {user_prefs['preferred_language']}")
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"Error building context string: {e}")
            return ""

    def _enhance_analysis_with_session_data(self, analysis: Dict[str, Any], 
                                          session: ConversationSession, 
                                          recent_turns: List[ConversationTurn]) -> Dict[str, Any]:
        """Enhance AI analysis with session-specific data"""
        try:
            # Check if this is a follow-up to a previous question
            if recent_turns and recent_turns[-1].role == "assistant":
                last_bot_message = recent_turns[-1].content
                if self._is_follow_up_response(analysis, last_bot_message):
                    analysis["is_follow_up"] = True
                    analysis["responding_to"] = self._extract_question_from_message(last_bot_message)
            
            # Check for repeated issues
            if self._is_repeated_issue(analysis, recent_turns):
                analysis["is_repeated_issue"] = True
                analysis["repetition_count"] = self._count_issue_repetitions(analysis, recent_turns)
            
            # Check for escalation patterns
            if self._is_escalation(analysis, recent_turns):
                analysis["is_escalation"] = True
                analysis["escalation_reason"] = self._identify_escalation_reason(analysis, recent_turns)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            return analysis

    def _is_follow_up_response(self, analysis: Dict[str, Any], last_bot_message: str) -> bool:
        """Check if current message is a response to a bot's question"""
        try:
            # Check if last bot message asked a question
            question_indicators = ["?", "please", "could you", "can you", "would you", "tell me"]
            is_question = any(indicator in last_bot_message.lower() for indicator in question_indicators)
            
            if not is_question:
                return False
            
            # Check if current message provides information
            info_indicators = ["yes", "no", "okay", "sure", "here", "it's", "the", "my"]
            provides_info = any(indicator in analysis.get("text", "").lower() for indicator in info_indicators)
            
            return provides_info
            
        except Exception as e:
            logger.error(f"Error checking follow-up response: {e}")
            return False

    def _extract_question_from_message(self, message: str) -> str:
        """Extract the question from a bot message"""
        try:
            # Simple extraction - look for question marks
            if "?" in message:
                parts = message.split("?")
                return parts[0].strip() + "?"
            
            # Look for question patterns
            question_patterns = [
                "Could you please",
                "Can you tell me",
                "Would you mind",
                "Please provide"
            ]
            
            for pattern in question_patterns:
                if pattern in message:
                    start_idx = message.find(pattern)
                    return message[start_idx:].strip()
            
            return message
            
        except Exception as e:
            logger.error(f"Error extracting question: {e}")
            return message

    def _is_repeated_issue(self, analysis: Dict[str, Any], recent_turns: List[ConversationTurn]) -> bool:
        """Check if this is a repeated issue"""
        try:
            current_intent = analysis.get("category", "")
            current_entities = analysis.get("entities", {})
            
            # Check recent user turns for similar intent
            for turn in recent_turns[-3:]:  # Check last 3 turns
                if turn.role == "user" and turn.ai_analysis:
                    if turn.ai_analysis.get("category") == current_intent:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking repeated issue: {e}")
            return False

    def _count_issue_repetitions(self, analysis: Dict[str, Any], recent_turns: List[ConversationTurn]) -> int:
        """Count how many times this issue has been mentioned"""
        try:
            current_intent = analysis.get("category", "")
            count = 0
            
            for turn in recent_turns:
                if turn.role == "user" and turn.ai_analysis:
                    if turn.ai_analysis.get("category") == current_intent:
                        count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting issue repetitions: {e}")
            return 1

    def _is_escalation(self, analysis: Dict[str, Any], recent_turns: List[ConversationTurn]) -> bool:
        """Check if this message indicates escalation"""
        try:
            # Check for escalation keywords
            escalation_keywords = [
                "manager", "supervisor", "escalate", "higher", "complaint", 
                "unhappy", "dissatisfied", "angry", "frustrated", "terrible"
            ]
            
            message_text = analysis.get("text", "").lower()
            has_escalation_keywords = any(keyword in message_text for keyword in escalation_keywords)
            
            # Check for increased urgency
            current_urgency = analysis.get("urgency", "medium")
            if current_urgency in ["high", "critical"]:
                return True
            
            # Check for repeated complaints
            if self._is_repeated_issue(analysis, recent_turns):
                repetition_count = self._count_issue_repetitions(analysis, recent_turns)
                if repetition_count >= 2:
                    return True
            
            return has_escalation_keywords
            
        except Exception as e:
            logger.error(f"Error checking escalation: {e}")
            return False

    def _identify_escalation_reason(self, analysis: Dict[str, Any], recent_turns: List[ConversationTurn]) -> str:
        """Identify the reason for escalation"""
        try:
            if analysis.get("urgency") in ["high", "critical"]:
                return "high_urgency"
            
            if self._is_repeated_issue(analysis, recent_turns):
                return "repeated_issue"
            
            # Check for dissatisfaction keywords
            dissatisfaction_keywords = ["unhappy", "dissatisfied", "angry", "frustrated"]
            message_text = analysis.get("text", "").lower()
            if any(keyword in message_text for keyword in dissatisfaction_keywords):
                return "user_dissatisfaction"
            
            return "general_escalation"
            
        except Exception as e:
            logger.error(f"Error identifying escalation reason: {e}")
            return "unknown"

    def _update_session_context(self, session_id: int, analysis: Dict[str, Any], turn_id: int):
        """Update session context with new information"""
        try:
            # Extract entities and update context
            entities = analysis.get("entities", {})
            
            for entity_type, entity_value in entities.items():
                if entity_value:
                    self._update_context_item(
                        session_id, "issue_details", entity_type, entity_value, turn_id
                    )
            
            # Update user preferences
            if analysis.get("language"):
                self._update_context_item(
                    session_id, "user_preferences", "preferred_language", 
                    analysis["language"], turn_id
                )
            
            # Update issue type
            if analysis.get("category"):
                self._update_context_item(
                    session_id, "issue_details", "issue_type", 
                    analysis["category"], turn_id
                )
            
            # Update urgency level
            if analysis.get("urgency"):
                self._update_context_item(
                    session_id, "issue_details", "urgency_level", 
                    analysis["urgency"], turn_id
                )
            
        except Exception as e:
            logger.error(f"Error updating session context: {e}")

    def _update_context_item(self, session_id: int, context_type: str, key: str, 
                           value: Any, source_turn: int):
        """Update a specific context item"""
        try:
            # Check if context item already exists
            existing = self.db.query(SessionContext).filter(
                SessionContext.session_id == session_id,
                SessionContext.context_type == context_type,
                SessionContext.context_key == key
            ).first()
            
            if existing:
                # Update existing context
                existing.context_value = value
                existing.source_turn = source_turn
                existing.updated_at = datetime.utcnow()
            else:
                # Create new context item
                new_context = SessionContext(
                    session_id=session_id,
                    context_type=context_type,
                    context_key=key,
                    context_value=value,
                    source_turn=source_turn
                )
                self.db.add(new_context)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating context item: {e}")

    def _generate_contextual_response(self, session: ConversationSession, 
                                    user_message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual response based on conversation history"""
        try:
            # Get session context and recent turns
            context = self._get_session_context(session.id)
            recent_turns = self._get_recent_conversation_turns(session.id, 3)
            
            # Check if this is a follow-up response
            if analysis.get("is_follow_up"):
                response = self._generate_follow_up_acknowledgment(analysis, context)
                return response
            
            # Check if this is a repeated issue
            if analysis.get("is_repeated_issue"):
                response = self._generate_repeated_issue_response(analysis, context, recent_turns)
                return response
            
            # Check if this is an escalation
            if analysis.get("is_escalation"):
                response = self._generate_escalation_response(analysis, context)
                return response
            
            # Generate appropriate follow-up question
            follow_up = self._generate_follow_up_question(session, analysis, context, recent_turns)
            
            # Generate base response
            base_response = self._generate_base_response(analysis, context)
            
            # Combine response with follow-up
            if follow_up:
                full_response = f"{base_response}\n\n{follow_up['question']}"
                return {
                    "message": full_response,
                    "follow_up_required": True,
                    "follow_up_type": follow_up["type"],
                    "context_summary": self._generate_context_summary(context)
                }
            else:
                return {
                    "message": base_response,
                    "follow_up_required": False,
                    "context_summary": self._generate_context_summary(context)
                }
            
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return self._get_fallback_response(session.language)

    def _generate_follow_up_acknowledgment(self, analysis: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment for follow-up responses"""
        try:
            # Extract what the user provided
            provided_info = analysis.get("entities", {})
            
            acknowledgment_parts = []
            
            if "order_number" in provided_info:
                acknowledgment_parts.append(f"Thank you for providing the order number: {provided_info['order_number']}.")
            
            if "product_name" in provided_info:
                acknowledgment_parts.append(f"I understand the issue is with: {provided_info['product_name']}.")
            
            if "date" in provided_info:
                acknowledgment_parts.append(f"Thank you for the date information.")
            
            if acknowledgment_parts:
                acknowledgment = " ".join(acknowledgment_parts)
                
                # Check if we have enough information to proceed
                if self._has_sufficient_information(context):
                    response = f"{acknowledgment} I have all the information I need. Let me create a ticket for you and our team will address this issue promptly."
                    return {
                        "message": response,
                        "follow_up_required": False,
                        "context_summary": self._generate_context_summary(context)
                    }
                else:
                    # Still need more information
                    next_question = self._get_next_required_information(context)
                    response = f"{acknowledgment} {next_question}"
                    return {
                        "message": response,
                        "follow_up_required": True,
                        "follow_up_type": "details",
                        "context_summary": self._generate_context_summary(context)
                    }
            
            return self._get_fallback_response("en")
            
        except Exception as e:
            logger.error(f"Error generating follow-up acknowledgment: {e}")
            return self._get_fallback_response("en")

    def _has_sufficient_information(self, context: Dict[str, Any]) -> bool:
        """Check if we have sufficient information to create a ticket"""
        try:
            issue_details = context.get("issue_details", {})
            
            # Basic requirements
            has_issue_type = "issue_type" in issue_details
            has_urgency = "urgency_level" in issue_details
            
            # Additional helpful info
            has_order_number = "order_number" in issue_details
            has_product = "product_name" in issue_details
            
            # For complaints, we need at least issue type and urgency
            return has_issue_type and has_urgency
            
        except Exception as e:
            logger.error(f"Error checking sufficient information: {e}")
            return False

    def _get_next_required_information(self, context: Dict[str, Any]) -> str:
        """Get the next piece of information needed"""
        try:
            issue_details = context.get("issue_details", {})
            
            if "order_number" not in issue_details:
                return "Could you please provide your order number or reference number?"
            
            if "product_name" not in issue_details:
                return "Could you please tell me which product or service this is about?"
            
            if "date" not in issue_details:
                return "When did this issue occur?"
            
            return "Could you please provide any additional details about the issue?"
            
        except Exception as e:
            logger.error(f"Error getting next required information: {e}")
            return "Could you please provide more details about your issue?"

    def _generate_repeated_issue_response(self, analysis: Dict[str, Any], 
                                        context: Dict[str, Any], 
                                        recent_turns: List[ConversationTurn]) -> Dict[str, Any]:
        """Generate response for repeated issues"""
        try:
            repetition_count = analysis.get("repetition_count", 1)
            
            if repetition_count == 2:
                response = "I understand this issue is important to you. Let me ensure I have all the details correct and escalate this to our team immediately."
            else:
                response = "I apologize for the continued inconvenience. This issue has been escalated to our senior support team who will contact you directly."
            
            # Add context summary
            context_summary = self._generate_context_summary(context)
            
            return {
                "message": response,
                "follow_up_required": False,
                "context_summary": context_summary
            }
            
        except Exception as e:
            logger.error(f"Error generating repeated issue response: {e}")
            return self._get_fallback_response("en")

    def _generate_escalation_response(self, analysis: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for escalation situations"""
        try:
            escalation_reason = analysis.get("escalation_reason", "unknown")
            
            if escalation_reason == "high_urgency":
                response = "I understand this is urgent. I'm escalating this issue to our priority support team who will contact you within the next 30 minutes."
            elif escalation_reason == "repeated_issue":
                response = "I apologize that this issue hasn't been resolved yet. I'm escalating this to our senior support team who will take immediate action."
            elif escalation_reason == "user_dissatisfaction":
                response = "I understand your frustration. Let me connect you with our customer success team who will personally handle this matter."
            else:
                response = "I'm escalating this issue to ensure it receives the attention it deserves. Our senior team will contact you shortly."
            
            context_summary = self._generate_context_summary(context)
            
            return {
                "message": response,
                "follow_up_required": False,
                "context_summary": context_summary
            }
            
        except Exception as e:
            logger.error(f"Error generating escalation response: {e}")
            return self._get_fallback_response("en")

    def _generate_follow_up_question(self, session: ConversationSession, analysis: Dict[str, Any], 
                                   context: Dict[str, Any], 
                                   recent_turns: List[ConversationTurn]) -> Optional[Dict[str, Any]]:
        """Generate appropriate follow-up question"""
        try:
            # Check if we already have sufficient information
            if self._has_sufficient_information(context):
                return None
            
            # Get brand-specific follow-up templates
            follow_up_templates = self._get_follow_up_templates(
                session.brand_id, analysis.get("category"), analysis.get("urgency")
            )
            
            if follow_up_templates:
                # Use brand-specific template
                template = follow_up_templates[0]  # Use highest priority
                return {
                    "question": template.template_text,
                    "type": template.follow_up_type
                }
            
            # Use default follow-up logic
            issue_details = context.get("issue_details", {})
            
            if "order_number" not in issue_details:
                return {
                    "question": "Could you please provide your order number or reference number?",
                    "type": "details"
                }
            
            if "product_name" not in issue_details:
                return {
                    "question": "Could you please tell me which product or service this is about?",
                    "type": "details"
                }
            
            if "date" not in issue_details:
                return {
                    "question": "When did this issue occur?",
                    "type": "details"
                }
            
            return {
                "question": "Could you please provide any additional details about the issue?",
                "type": "details"
            }
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None

    def _get_follow_up_templates(self, brand_id: int, intent: str, urgency: str) -> List[FollowUpTemplate]:
        """Get brand-specific follow-up templates"""
        try:
            templates = self.db.query(FollowUpTemplate).filter(
                FollowUpTemplate.brand_id == brand_id,
                FollowUpTemplate.trigger_intent == intent,
                FollowUpTemplate.is_active == True
            ).order_by(FollowUpTemplate.priority.asc()).all()
            
            return templates
            
        except Exception as e:
            logger.error(f"Error getting follow-up templates: {e}")
            return []

    def _generate_base_response(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate base response for the analysis"""
        try:
            category = analysis.get("category", "complaint")
            urgency = analysis.get("urgency", "medium")
            
            if category == "complaint":
                if urgency in ["high", "critical"]:
                    return "I understand this is a serious issue and I'm here to help resolve it immediately."
                else:
                    return "I understand your concern and I'm here to help resolve this issue."
            
            elif category == "feedback":
                return "Thank you for your feedback. We value your input and will use it to improve our services."
            
            elif category == "support":
                return "I'm here to help you with any questions or support you need."
            
            else:
                return "Thank you for your message. I'm here to assist you."
            
        except Exception as e:
            logger.error(f"Error generating base response: {e}")
            return "Thank you for your message. I'm here to help."

    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a summary of the conversation context"""
        try:
            summary_parts = []
            
            issue_details = context.get("issue_details", {})
            if issue_details:
                if "issue_type" in issue_details:
                    summary_parts.append(f"Issue: {issue_details['issue_type']}")
                if "urgency_level" in issue_details:
                    summary_parts.append(f"Urgency: {issue_details['urgency_level']}")
                if "order_number" in issue_details:
                    summary_parts.append(f"Order: {issue_details['order_number']}")
                if "product_name" in issue_details:
                    summary_parts.append(f"Product: {issue_details['product_name']}")
            
            return " | ".join(summary_parts) if summary_parts else "New conversation"
            
        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            return "Conversation in progress"

    def _store_for_learning(self, session: ConversationSession, user_message: str, 
                           analysis: Dict[str, Any], response: Dict[str, Any]):
        """Store interaction for learning"""
        try:
            # Store in AI learning data
            learning_data = AILearningData(
                brand_id=session.brand_id,
                ticket_id=session.ticket_id,
                user_message=user_message,
                ai_prediction=analysis,
                language=session.language,
                channel=session.channel
            )
            
            self.db.add(learning_data)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing for learning: {e}")

    def _get_fallback_response(self, language: str) -> Dict[str, Any]:
        """Get fallback response when processing fails"""
        fallback_responses = {
            "en": "I apologize, but I'm having trouble processing your message right now. Please try again or contact our support team.",
            "hi": "माफ़ कीजिए, लेकिन मुझे आपका संदेश संसाधित करने में समस्या हो रही है। कृपया फिर से कोशिश करें या हमारी सहायता टीम से संपर्क करें।",
            "es": "Lo siento, pero estoy teniendo problemas para procesar su mensaje en este momento. Por favor, inténtelo de nuevo o contacte a nuestro equipo de soporte.",
            "fr": "Je m'excuse, mais j'ai des difficultés à traiter votre message en ce moment. Veuillez réessayer ou contacter notre équipe de support."
        }
        
        return {
            "message": fallback_responses.get(language, fallback_responses["en"]),
            "follow_up_required": False
        }

    def get_conversation_history(self, session_id: str, brand_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            session = self.db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id,
                ConversationSession.brand_id == brand_id
            ).first()
            
            if not session:
                return []
            
            turns = self.db.query(ConversationTurn).filter(
                ConversationTurn.session_id == session.id
            ).order_by(ConversationTurn.turn_number.desc()).limit(limit).all()
            
            return [
                {
                    "turn_number": turn.turn_number,
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.created_at.isoformat(),
                    "ai_analysis": turn.ai_analysis
                }
                for turn in reversed(turns)  # Return in chronological order
            ]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def resume_conversation(self, session_id: str, brand_id: int) -> Dict[str, Any]:
        """Resume an existing conversation"""
        try:
            session = self.db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id,
                ConversationSession.brand_id == brand_id
            ).first()
            
            if not session:
                return {"error": "Session not found"}
            
            # Get recent context
            context = self._get_session_context(session.id)
            recent_turns = self._get_recent_conversation_turns(session.id, 3)
            
            # Generate resumption message
            if recent_turns:
                last_turn = recent_turns[-1]
                if last_turn.role == "assistant" and last_turn.follow_up_required:
                    # Continue from where we left off
                    return {
                        "message": f"Welcome back! {last_turn.content}",
                        "follow_up_required": True,
                        "follow_up_type": last_turn.follow_up_type
                    }
                else:
                    # General resumption
                    context_summary = self._generate_context_summary(context)
                    return {
                        "message": f"Welcome back! I see we were discussing: {context_summary}. How can I help you further?",
                        "follow_up_required": False
                    }
            else:
                return {
                    "message": "Welcome back! How can I help you today?",
                    "follow_up_required": False
                }
            
        except Exception as e:
            logger.error(f"Error resuming conversation: {e}")
            return {"error": str(e)}

    def close_conversation(self, session_id: str, brand_id: int, reason: str = "completed") -> bool:
        """Close a conversation session"""
        try:
            session = self.db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id,
                ConversationSession.brand_id == brand_id
            ).first()
            
            if session:
                session.status = "completed" if reason == "completed" else "abandoned"
                session.last_activity = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing conversation: {e}")
            return False