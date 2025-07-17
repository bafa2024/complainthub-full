# backend/app/core/ai_engine.py

import openai
import os
from ..config.settings import settings
from ..schemas import TicketCategoryEnum, TicketUrgencyEnum
import logging
import json
import traceback
from typing import Dict, Any, Optional, List, Tuple
import requests
from google.cloud import language_v1
from google.cloud.language_v1 import Document
import numpy as np
from datetime import datetime, timedelta
import pickle
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import re
from google.cloud import translate_v2 as translate
from google.cloud import language_v1
from google.cloud.language_v1 import Document
import langdetect
from langdetect import detect, DetectorFactory

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        try:
            # Try to get OpenAI API key from settings method
            self.openai_api_key = settings.OPENAI_API_KEY
            self.has_openai_key = bool(self.openai_api_key and self.openai_api_key.strip())
            
            if self.has_openai_key:
                openai.api_key = self.openai_api_key
                logger.info("OpenAI API key configured successfully")
            else:
                logger.warning("OpenAI API key not found. AI features will use fallback responses.")
            
            self.model = "gpt-3.5-turbo"  # Using a modern, cost-effective chat model
            
            # Initialize Google Cloud Natural Language client
            self.google_api_key = settings.GOOGLE_API_KEY
            self.has_google_key = bool(self.google_api_key and self.google_api_key.strip())
            
            if self.has_google_key:
                try:
                    self.language_client = language_v1.LanguageServiceClient()
                    self.translate_client = translate.Client()
                    logger.info("Google Cloud Natural Language and Translate clients initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize Google Cloud clients: {e}")
                    self.has_google_key = False
            else:
                logger.warning("Google Cloud API key not found. Advanced NLP and translation features will be limited.")
                self.has_google_key = False
            
            # Initialize language detection
            DetectorFactory.seed = 0  # For consistent results
            
            # Supported languages mapping
            self.supported_languages = {
                "en": "English",
                "hi": "Hindi",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese",
                "ar": "Arabic",
                "tr": "Turkish",
                "nl": "Dutch",
                "pl": "Polish",
                "sv": "Swedish",
                "da": "Danish",
                "no": "Norwegian",
                "fi": "Finnish",
                "cs": "Czech",
                "hu": "Hungarian",
                "ro": "Romanian",
                "bg": "Bulgarian",
                "hr": "Croatian",
                "sk": "Slovak",
                "sl": "Slovenian",
                "et": "Estonian",
                "lv": "Latvian",
                "lt": "Lithuanian",
                "mt": "Maltese",
                "el": "Greek"
            }
            
            # Initialize ML models
            self.ml_models = {}
            self.vectorizers = {}
            self.ml_model_metadata = {}
            self.load_ml_models()
            
            # Self-learning cache
            self.learning_cache = {
                "brand_patterns": {},
                "user_preferences": {},
                "conversation_templates": {},
                "response_effectiveness": {},
                "language_preferences": {}
            }
            
        except Exception as e:
            logger.error(f"Error initializing AIEngine: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.has_openai_key = False
            self.has_google_key = False
            self.model = "gpt-3.5-turbo"
            self.ml_models = {}
            self.vectorizers = {}
            self.ml_model_metadata = {}
            self.learning_cache = {}

    def load_ml_models(self):
        """Load trained ML models from disk"""
        try:
            model_path = "backend/ml_models"
            if not os.path.exists(model_path):
                os.makedirs(model_path)
                logger.info("Created ML models directory")
                return
            
            # Load intent classification model
            intent_model_path = os.path.join(model_path, "intent_classifier.pkl")
            if os.path.exists(intent_model_path):
                self.ml_models["intent_classifier"] = joblib.load(intent_model_path)
                logger.info("Loaded intent classification model")
            
            # Load urgency classification model
            urgency_model_path = os.path.join(model_path, "urgency_classifier.pkl")
            if os.path.exists(urgency_model_path):
                self.ml_models["urgency_classifier"] = joblib.load(urgency_model_path)
                logger.info("Loaded urgency classification model")
            
            # Load vectorizers
            vectorizer_path = os.path.join(model_path, "tfidf_vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                self.vectorizers["tfidf"] = joblib.load(vectorizer_path)
                logger.info("Loaded TF-IDF vectorizer")
            
            # Load model metadata
            metadata_path = os.path.join(model_path, "model_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.ml_model_metadata = json.load(f)
                logger.info("Loaded model metadata")
                
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")

    def save_ml_models(self):
        """Save trained ML models to disk"""
        try:
            model_path = "backend/ml_models"
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            
            # Save intent classifier
            if "intent_classifier" in self.ml_models:
                joblib.dump(self.ml_models["intent_classifier"], 
                           os.path.join(model_path, "intent_classifier.pkl"))
            
            # Save urgency classifier
            if "urgency_classifier" in self.ml_models:
                joblib.dump(self.ml_models["urgency_classifier"], 
                           os.path.join(model_path, "urgency_classifier.pkl"))
            
            # Save vectorizer
            if "tfidf" in self.vectorizers:
                joblib.dump(self.vectorizers["tfidf"], 
                           os.path.join(model_path, "tfidf_vectorizer.pkl"))
            
            # Save metadata
            with open(os.path.join(model_path, "model_metadata.json"), 'w') as f:
                json.dump(self.ml_model_metadata, f, indent=2)
                
            logger.info("ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving ML models: {e}")

    def train_ml_models(self, training_data: List[Dict[str, Any]]):
        """Train ML models with new data"""
        try:
            if not training_data:
                logger.warning("No training data provided")
                return
            
            # Prepare training data
            texts = [item["text"] for item in training_data]
            intent_labels = [item["intent"] for item in training_data]
            urgency_labels = [item["urgency"] for item in training_data]
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=2
            )
            
            # Fit and transform text data
            X = vectorizer.fit_transform(texts)
            
            # Train intent classifier
            intent_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            intent_classifier.fit(X, intent_labels)
            
            # Train urgency classifier
            urgency_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            urgency_classifier.fit(X, urgency_labels)
            
            # Store models
            self.ml_models["intent_classifier"] = intent_classifier
            self.ml_models["urgency_classifier"] = urgency_classifier
            self.vectorizers["tfidf"] = vectorizer
            
            # Update metadata
            self.ml_model_metadata = {
                "last_trained": datetime.utcnow().isoformat(),
                "training_samples": len(training_data),
                "intent_accuracy": accuracy_score(intent_labels, intent_classifier.predict(X)),
                "urgency_accuracy": accuracy_score(urgency_labels, urgency_classifier.predict(X))
            }
            
            # Save models
            self.save_ml_models()
            
            logger.info(f"ML models trained successfully with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Error training ML models: {e}")

    def predict_with_ml(self, text: str) -> Dict[str, Any]:
        """Predict intent and urgency using ML models"""
        try:
            if not self.ml_models or "tfidf" not in self.vectorizers:
                return {
                    "intent": "complaint",
                    "urgency": "medium",
                    "confidence": 0.5
                }
            
            # Vectorize text
            X = self.vectorizers["tfidf"].transform([text])
            
            # Predict intent
            intent_pred = self.ml_models["intent_classifier"].predict(X)[0]
            intent_proba = np.max(self.ml_models["intent_classifier"].predict_proba(X))
            
            # Predict urgency
            urgency_pred = self.ml_models["urgency_classifier"].predict(X)[0]
            urgency_proba = np.max(self.ml_models["urgency_classifier"].predict_proba(X))
            
            return {
                "intent": intent_pred,
                "urgency": urgency_pred,
                "intent_confidence": float(intent_proba),
                "urgency_confidence": float(urgency_proba),
                "overall_confidence": float((intent_proba + urgency_proba) / 2)
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return {
                "intent": "complaint",
                "urgency": "medium",
                "confidence": 0.5
            }

    def _get_chat_completion(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """Helper function to get a chat completion from OpenAI with enhanced context."""
        try:
            if not self.has_openai_key:
                logger.info("OpenAI not available, returning fallback response")
                return "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?"
            
            # Enhance system prompt with learning context
            enhanced_system_prompt = f"{system_prompt}\n\nContext: {context}" if context else system_prompt
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
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

    def analyze_sentiment_and_toxicity(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using Google Cloud Natural Language API for sentiment and toxicity.
        """
        try:
            if not self.has_google_key:
                logger.info("Google Cloud not available, returning fallback analysis")
                return {
                    "sentiment_score": 0.0,
                    "sentiment_magnitude": 0.0,
                    "toxicity_score": 0.0,
                    "categories": [],
                    "entities": []
                }
            
            # Create document
            document = Document(content=text, type_=Document.Type.PLAIN_TEXT)
            
            # Analyze sentiment
            sentiment_response = self.language_client.analyze_sentiment(request={'document': document})
            sentiment = sentiment_response.document_sentiment
            
            # Analyze entities
            entities_response = self.language_client.analyze_entities(request={'document': document})
            entities = [
                {
                    "name": entity.name,
                    "type": entity.type_.name,
                    "salience": entity.salience
                }
                for entity in entities_response.entities
            ]
            
            # Analyze content classification
            classification_response = self.language_client.classify_text(request={'document': document})
            categories = [
                {
                    "name": category.name,
                    "confidence": category.confidence
                }
                for category in classification_response.categories
            ]
            
            # Enhanced toxicity detection
            toxicity_score = self._calculate_toxicity_score(text)
            
            return {
                "sentiment_score": sentiment.score,
                "sentiment_magnitude": sentiment.magnitude,
                "toxicity_score": toxicity_score,
                "categories": categories,
                "entities": entities
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "sentiment_score": 0.0,
                "sentiment_magnitude": 0.0,
                "toxicity_score": 0.0,
                "categories": [],
                "entities": []
            }

    def _calculate_toxicity_score(self, text: str) -> float:
        """Calculate toxicity score using enhanced keyword and pattern matching"""
        try:
            # Enhanced toxic patterns
            toxic_patterns = [
                r'\b(abuse|abusive)\b',
                r'\b(hate|hatred)\b',
                r'\b(violent|violence)\b',
                r'\b(threat|threatening)\b',
                r'\b(insult|insulting)\b',
                r'\b(profanity|curse|swear)\b',
                r'\b(racist|racism)\b',
                r'\b(sexist|sexism)\b',
                r'\b(discriminat|discrimination)\b',
                r'\b(harass|harassment)\b'
            ]
            
            text_lower = text.lower()
            toxicity_count = 0
            
            for pattern in toxic_patterns:
                if re.search(pattern, text_lower):
                    toxicity_count += 1
            
            # Normalize score
            max_patterns = len(toxic_patterns)
            toxicity_score = min(toxicity_count / max_patterns, 1.0)
            
            # Apply sentiment penalty
            if hasattr(self, 'language_client') and self.has_google_key:
                try:
                    document = Document(content=text, type_=Document.Type.PLAIN_TEXT)
                    sentiment_response = self.language_client.analyze_sentiment(request={'document': document})
                    sentiment_score = sentiment_response.document_sentiment.score
                    
                    # Increase toxicity for very negative sentiment
                    if sentiment_score < -0.5:
                        toxicity_score = min(toxicity_score + 0.2, 1.0)
                except:
                    pass
            
            return toxicity_score
            
        except Exception as e:
            logger.error(f"Error calculating toxicity score: {e}")
            return 0.0

    def classify_intent_and_extract_details(self, text: str, brand_context: str = "") -> dict:
        """
        Analyzes the user's text to classify its intent, urgency, sentiment,
        and extracts key details for ticket creation with enhanced ML capabilities.
        """
        try:
            # First, get advanced NLP analysis
            nlp_analysis = self.analyze_sentiment_and_toxicity(text)
            
            # Get ML predictions
            ml_predictions = self.predict_with_ml(text)
            
            # Combine ML and OpenAI analysis
            if not self.has_openai_key:
                logger.info("OpenAI not available, using ML predictions")
                return {
                    "category": ml_predictions["intent"],
                    "urgency": ml_predictions["urgency"],
                    "abuse_flag": nlp_analysis["toxicity_score"] > 0.5,
                    "title": self._generate_title_from_text(text),
                    "extracted_details": self._extract_details_from_text(text),
                    "sentiment_score": nlp_analysis["sentiment_score"],
                    "sentiment_magnitude": nlp_analysis["sentiment_magnitude"],
                    "toxicity_score": nlp_analysis["toxicity_score"],
                    "entities": nlp_analysis["entities"],
                    "ml_confidence": ml_predictions["overall_confidence"]
                }
            
            # Enhanced system prompt with brand context and learning
            system_prompt = f"""
                You are an expert AI assistant for a complaint management system.
                Your task is to analyze the user's message and extract key information in a structured JSON format.
                
                Brand Context: {brand_context}
                
                The JSON output must contain the following fields:
                - "category": Classify the user's intent into one of these categories: {', '.join([e.value for e in TicketCategoryEnum])}.
                - "urgency": Assess the urgency from the user's language. Classify into one of: {', '.join([e.value for e in TicketUrgencyEnum])}.
                - "abuse_flag": Set to true if the user's language is abusive, toxic, or contains profanity, otherwise false.
                - "title": A concise, 5-10 word summary of the user's issue.
                - "extracted_details": Any specific details mentioned like product names, order numbers, dates, or locations.
                - "suggested_response": A suggested response template for this type of issue.

                Analyze the user's text and provide only the JSON object as a response.
            """
            
            user_prompt = f"Analyze the following text: '{text}'"

            response_json_str = self._get_chat_completion(system_prompt, user_prompt, brand_context)
            
            # Clean the response to ensure it's valid JSON
            if response_json_str.startswith("```json"):
                response_json_str = response_json_str[7:-4].strip()
            elif response_json_str.startswith("```"):
                response_json_str = response_json_str[3:-3].strip()

            parsed_response = json.loads(response_json_str)
            
            # Validate enums to prevent errors
            if parsed_response.get("category") not in [e.value for e in TicketCategoryEnum]:
                logger.warning(f"Invalid category '{parsed_response.get('category')}', using ML prediction")
                parsed_response["category"] = ml_predictions["intent"]
            
            if parsed_response.get("urgency") not in [e.value for e in TicketUrgencyEnum]:
                logger.warning(f"Invalid urgency '{parsed_response.get('urgency')}', using ML prediction")
                parsed_response["urgency"] = ml_predictions["urgency"]
            
            # Combine with ML predictions for confidence
            parsed_response["ml_confidence"] = ml_predictions["overall_confidence"]
            parsed_response["sentiment_score"] = nlp_analysis["sentiment_score"]
            parsed_response["sentiment_magnitude"] = nlp_analysis["sentiment_magnitude"]
            parsed_response["toxicity_score"] = nlp_analysis["toxicity_score"]
            parsed_response["entities"] = nlp_analysis["entities"]
            
            # Store for learning
            self._store_prediction_for_learning(text, parsed_response, brand_context)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "category": TicketCategoryEnum.complaint.value,
                "urgency": TicketUrgencyEnum.medium.value,
                "abuse_flag": False,
                "title": "Complaint submitted via chat",
                "extracted_details": text,
                "sentiment_score": 0.0,
                "sentiment_magnitude": 0.0,
                "toxicity_score": 0.0,
                "entities": [],
                "ml_confidence": 0.5
            }

    def _generate_title_from_text(self, text: str) -> str:
        """Generate a title from text using simple NLP"""
        try:
            # Extract key phrases
            words = text.split()
            if len(words) <= 5:
                return text[:50]
            
            # Find important words (longer words, not common stop words)
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            important_words = [word for word in words if len(word) > 3 and word.lower() not in stop_words]
            
            if important_words:
                title = " ".join(important_words[:5])
                return title[:50]
            else:
                return text[:50]
                
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return text[:50]

    def _extract_details_from_text(self, text: str) -> str:
        """Extract key details from text"""
        try:
            # Extract patterns like order numbers, emails, phone numbers
            patterns = {
                'order_number': r'\b[A-Z0-9]{6,12}\b',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'\b\+?[\d\s\-\(\)]{10,15}\b',
                'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            }
            
            details = []
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    details.extend(matches)
            
            return ", ".join(details) if details else text[:200]
            
        except Exception as e:
            logger.error(f"Error extracting details: {e}")
            return text[:200]

    def _store_prediction_for_learning(self, text: str, prediction: Dict, brand_context: str):
        """Store prediction for future learning"""
        try:
            # Create learning entry
            learning_entry = {
                "text": text,
                "prediction": prediction,
                "brand_context": brand_context,
                "timestamp": datetime.utcnow().isoformat(),
                "text_hash": hashlib.md5(text.encode()).hexdigest()
            }
            
            # Store in cache (in production, this would go to database)
            if "prediction_history" not in self.learning_cache:
                self.learning_cache["prediction_history"] = []
            
            self.learning_cache["prediction_history"].append(learning_entry)
            
            # Keep only last 1000 entries
            if len(self.learning_cache["prediction_history"]) > 1000:
                self.learning_cache["prediction_history"] = self.learning_cache["prediction_history"][-1000:]
                
        except Exception as e:
            logger.error(f"Error storing prediction for learning: {e}")

    def generate_follow_up_question(self, conversation_history: list, context: str = "", language: str = "en") -> str:
        """
        Based on the conversation history, generate a relevant follow-up question
        to gather any missing information needed for a complete ticket with enhanced learning.
        """
        try:
            if not self.has_openai_key:
                logger.info("OpenAI not available, returning fallback question")
                return self._get_enhanced_fallback_question(conversation_history, language)
            
            # Analyze conversation for missing information
            missing_info = self._analyze_missing_information(conversation_history)
            
            system_prompt = f"""
                You are a conversational AI for a customer support bot.
                Your goal is to gather enough information to file a complete complaint ticket.
                
                Context: {context}
                Missing Information: {missing_info}
                
                Based on the conversation so far, ask a single, clear, and concise question 
                to get the most important missing information.
                
                Do not greet the user. Just ask the question.
                Make it specific and actionable.
            """
            
            # We only need the user's messages to formulate the next question
            user_conversation = "\n".join([f"User: {turn['content']}" for turn in conversation_history if turn['role'] == 'user'])
            
            user_prompt = f"Here is the conversation so far:\n{user_conversation}\n\nWhat is the best follow-up question to ask?"

            return self._get_chat_completion(system_prompt, user_prompt, context)
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_enhanced_fallback_question(conversation_history, language)

    def _analyze_missing_information(self, conversation_history: list) -> str:
        """Analyze conversation to identify missing information"""
        try:
            user_messages = [turn['content'] for turn in conversation_history if turn['role'] == 'user']
            full_text = " ".join(user_messages).lower()
            
            missing_info = []
            
            # Check for common missing information
            if not re.search(r'\b(order|order\s*#|order\s*number)\b', full_text):
                missing_info.append("order number")
            
            if not re.search(r'\b(email|e-mail)\b', full_text):
                missing_info.append("email address")
            
            if not re.search(r'\b(date|when|time)\b', full_text):
                missing_info.append("date/time of incident")
            
            if not re.search(r'\b(phone|mobile|contact)\b', full_text):
                missing_info.append("phone number")
            
            if not re.search(r'\b(location|where|place)\b', full_text):
                missing_info.append("location")
            
            if not re.search(r'\b(product|item|service)\b', full_text):
                missing_info.append("product/service details")
            
            return ", ".join(missing_info) if missing_info else "general details"
            
        except Exception as e:
            logger.error(f"Error analyzing missing information: {e}")
            return "general details"

    def _get_enhanced_fallback_question(self, conversation_history: list, language: str) -> str:
        """Get enhanced fallback question based on conversation analysis"""
        try:
            missing_info = self._analyze_missing_information(conversation_history)
            
            fallback_questions = {
                "en": {
                    "order number": "Could you please provide the order number for your purchase?",
                    "email address": "What is the email address associated with your account?",
                    "date/time of incident": "Can you tell me the date and time the incident occurred?",
                    "phone number": "Could you provide your contact phone number?",
                    "location": "Where did this incident take place?",
                    "product/service details": "Could you provide more details about the product or service?",
                    "general details": "Could you please provide more details about your issue?"
                },
                "hi": {
                    "order number": "कृपया अपने खरीदारी का ऑर्डर नंबर प्रदान करें?",
                    "email address": "आपके खाते से जुड़ा ईमेल पता क्या है?",
                    "date/time of incident": "क्या आप बता सकते हैं कि यह घटना कब हुई?",
                    "phone number": "क्या आप अपना संपर्क फोन नंबर दे सकते हैं?",
                    "location": "यह घटना कहाँ हुई?",
                    "product/service details": "क्या आप उत्पाद या सेवा के बारे में अधिक विवरण दे सकते हैं?",
                    "general details": "कृपया अपने मुद्दे के बारे में अधिक विवरण दें?"
                }
            }
            
            questions = fallback_questions.get(language, fallback_questions["en"])
            
            # Find the most relevant question
            for info_type, question in questions.items():
                if info_type in missing_info:
                    return question
            
            return questions["general details"]
            
        except Exception as e:
            logger.error(f"Error getting enhanced fallback question: {e}")
            return "Could you please provide more details about your issue?"

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the input text using multiple methods.
        Returns detailed language information including confidence scores.
        """
        try:
            if not text or not text.strip():
                return {
                    "language_code": "en",
                    "language_name": "English",
                    "confidence": 1.0,
                    "method": "fallback"
                }
            
            # Method 1: Google Cloud Natural Language API (most accurate)
            if self.has_google_key:
                try:
                    document = Document(content=text, type_=Document.Type.PLAIN_TEXT)
                    response = self.language_client.analyze_sentiment(request={'document': document})
                    
                    # Extract language from response
                    if hasattr(response, 'language') and response.language:
                        language_code = response.language
                        language_name = self.supported_languages.get(language_code, language_code)
                        
                        return {
                            "language_code": language_code,
                            "language_name": language_name,
                            "confidence": 0.95,
                            "method": "google_cloud"
                        }
                except Exception as e:
                    logger.warning(f"Google Cloud language detection failed: {e}")
            
            # Method 2: langdetect library (fallback)
            try:
                detected_lang = detect(text)
                language_name = self.supported_languages.get(detected_lang, detected_lang)
                
                # Get confidence from langdetect
                from langdetect import detect_langs
                lang_scores = detect_langs(text)
                confidence = max([lang.prob for lang in lang_scores]) if lang_scores else 0.8
                
                return {
                    "language_code": detected_lang,
                    "language_name": language_name,
                    "confidence": confidence,
                    "method": "langdetect"
                }
            except Exception as e:
                logger.warning(f"langdetect failed: {e}")
            
            # Method 3: Simple pattern matching (last resort)
            language_code = self._detect_language_by_patterns(text)
            language_name = self.supported_languages.get(language_code, language_code)
            
            return {
                "language_code": language_code,
                "language_name": language_name,
                "confidence": 0.6,
                "method": "pattern_matching"
            }
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return {
                "language_code": "en",
                "language_name": "English",
                "confidence": 1.0,
                "method": "fallback"
            }

    def _detect_language_by_patterns(self, text: str) -> str:
        """Detect language using simple pattern matching"""
        try:
            text_lower = text.lower()
            
            # Hindi patterns
            hindi_patterns = [r'[क-ह]', r'[अ-औ]', r'[ा-ौ]', r'[ं-ः]']
            for pattern in hindi_patterns:
                if re.search(pattern, text):
                    return "hi"
            
            # Spanish patterns
            spanish_words = ['hola', 'gracias', 'por favor', 'buenos días', 'buenas noches']
            if any(word in text_lower for word in spanish_words):
                return "es"
            
            # French patterns
            french_words = ['bonjour', 'merci', 's\'il vous plaît', 'au revoir']
            if any(word in text_lower for word in french_words):
                return "fr"
            
            # German patterns
            german_words = ['hallo', 'danke', 'bitte', 'auf wiedersehen']
            if any(word in text_lower for word in german_words):
                return "de"
            
            # Default to English
            return "en"
            
        except Exception as e:
            logger.error(f"Error in pattern-based language detection: {e}")
            return "en"

    def translate_text(self, text: str, target_language: str = "en", source_language: str = None) -> Dict[str, Any]:
        """
        Translate text to target language using Google Cloud Translate API.
        Returns detailed translation information including confidence scores.
        """
        try:
            if not text or not text.strip():
                return {
                    "translated_text": text,
                    "source_language": source_language or "en",
                    "target_language": target_language,
                    "confidence": 1.0,
                    "method": "no_translation_needed"
                }
            
            # Detect source language if not provided
            if not source_language:
                detection_result = self.detect_language(text)
                source_language = detection_result["language_code"]
            
            # If source and target are the same, no translation needed
            if source_language == target_language:
                return {
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 1.0,
                    "method": "no_translation_needed"
                }
            
            # Method 1: Google Cloud Translate API (most accurate)
            if self.has_google_key:
                try:
                    result = self.translate_client.translate(
                        text,
                        target_language=target_language,
                        source_language=source_language
                    )
                    
                    return {
                        "translated_text": result["translatedText"],
                        "source_language": result["detectedSourceLanguage"] if "detectedSourceLanguage" in result else source_language,
                        "target_language": target_language,
                        "confidence": 0.95,
                        "method": "google_translate"
                    }
                except Exception as e:
                    logger.warning(f"Google Cloud translation failed: {e}")
            
            # Method 2: Simple translation mapping (fallback)
            translated_text = self._simple_translate(text, source_language, target_language)
            
            return {
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "confidence": 0.7,
                "method": "simple_mapping"
            }
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "confidence": 0.0,
                "method": "error"
            }

    def _simple_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simple translation using predefined mappings"""
        try:
            # Common phrases translation mapping
            translations = {
                "en-hi": {
                    "hello": "नमस्ते",
                    "help": "मदद",
                    "complaint": "शिकायत",
                    "service": "सेवा",
                    "problem": "समस्या",
                    "thank you": "धन्यवाद",
                    "sorry": "माफ़ करें",
                    "good": "अच्छा",
                    "bad": "बुरा",
                    "customer": "ग्राहक"
                },
                "hi-en": {
                    "नमस्ते": "hello",
                    "मदद": "help",
                    "शिकायत": "complaint",
                    "सेवा": "service",
                    "समस्या": "problem",
                    "धन्यवाद": "thank you",
                    "माफ़ करें": "sorry",
                    "अच्छा": "good",
                    "बुरा": "bad",
                    "ग्राहक": "customer"
                },
                "en-es": {
                    "hello": "hola",
                    "help": "ayuda",
                    "complaint": "queja",
                    "service": "servicio",
                    "problem": "problema",
                    "thank you": "gracias",
                    "sorry": "lo siento",
                    "good": "bueno",
                    "bad": "malo",
                    "customer": "cliente"
                },
                "es-en": {
                    "hola": "hello",
                    "ayuda": "help",
                    "queja": "complaint",
                    "servicio": "service",
                    "problema": "problem",
                    "gracias": "thank you",
                    "lo siento": "sorry",
                    "bueno": "good",
                    "malo": "bad",
                    "cliente": "customer"
                }
            }
            
            key = f"{source_lang}-{target_lang}"
            if key in translations:
                translated_text = text
                for source_word, target_word in translations[key].items():
                    translated_text = re.sub(r'\b' + re.escape(source_word) + r'\b', target_word, translated_text, flags=re.IGNORECASE)
                return translated_text
            
            # If no mapping found, return original text
            return text
            
        except Exception as e:
            logger.error(f"Error in simple translation: {e}")
            return text

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages with their codes and names"""
        return {
            "languages": self.supported_languages,
            "total_count": len(self.supported_languages),
            "primary_language": "en",
            "detection_methods": ["google_cloud", "langdetect", "pattern_matching"],
            "translation_methods": ["google_translate", "simple_mapping"]
        }

    def auto_detect_and_translate(self, text: str, target_language: str = "en") -> Dict[str, Any]:
        """
        Automatically detect the language of text and translate to target language.
        This is the main method for multilingual processing.
        """
        try:
            # Step 1: Detect language
            detection_result = self.detect_language(text)
            
            # Step 2: Translate if needed
            translation_result = self.translate_text(
                text, 
                target_language=target_language,
                source_language=detection_result["language_code"]
            )
            
            return {
                "original_text": text,
                "detected_language": detection_result,
                "translation": translation_result,
                "processing_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in auto detect and translate: {e}")
            return {
                "original_text": text,
                "detected_language": {
                    "language_code": "en",
                    "language_name": "English",
                    "confidence": 0.0,
                    "method": "error"
                },
                "translation": {
                    "translated_text": text,
                    "source_language": "en",
                    "target_language": target_language,
                    "confidence": 0.0,
                    "method": "error"
                },
                "processing_time": datetime.utcnow().isoformat()
            }

    def process_multilingual_message(self, text: str, brand_context: str = "", target_language: str = "en") -> Dict[str, Any]:
        """
        Process a message in any language: detect, translate, and analyze.
        This is the complete multilingual processing pipeline.
        """
        try:
            # Step 1: Auto detect and translate
            multilingual_result = self.auto_detect_and_translate(text, target_language)
            
            # Step 2: Analyze the translated text
            analysis_result = self.classify_intent_and_extract_details(
                multilingual_result["translation"]["translated_text"], 
                brand_context
            )
            
            # Step 3: Get sentiment analysis
            sentiment_result = self.analyze_sentiment_and_toxicity(
                multilingual_result["translation"]["translated_text"]
            )
            
            return {
                "multilingual_processing": multilingual_result,
                "ai_analysis": analysis_result,
                "sentiment_analysis": sentiment_result,
                "processing_summary": {
                    "original_language": multilingual_result["detected_language"]["language_code"],
                    "target_language": target_language,
                    "translation_confidence": multilingual_result["translation"]["confidence"],
                    "detection_confidence": multilingual_result["detected_language"]["confidence"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in multilingual message processing: {e}")
            return {
                "error": str(e),
                "original_text": text,
                "target_language": target_language
            }

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning data"""
        try:
            return {
                "learning_cache_size": len(self.learning_cache),
                "brand_patterns_count": len(self.learning_cache.get("brand_patterns", {})),
                "user_preferences_count": len(self.learning_cache.get("user_preferences", {})),
                "conversation_templates_count": len(self.learning_cache.get("conversation_templates", {})),
                "response_effectiveness_count": len(self.learning_cache.get("response_effectiveness", {})),
                "language_preferences_count": len(self.learning_cache.get("language_preferences", {})),
                "ml_model_metadata": self.ml_model_metadata,
                "supported_languages": len(self.supported_languages)
            }
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {}

    def retrain_models(self, force: bool = False) -> Dict[str, Any]:
        """Retrain ML models with accumulated data"""
        try:
            prediction_history = self.learning_cache.get("prediction_history", [])
            
            if len(prediction_history) < 50 and not force:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 50 samples, have {len(prediction_history)}"
                }
            
            # Prepare training data
            training_data = []
            for entry in prediction_history:
                training_data.append({
                    "text": entry["text"],
                    "intent": entry["prediction"].get("category", "complaint"),
                    "urgency": entry["prediction"].get("urgency", "medium")
                })
            
            # Train models
            self.train_ml_models(training_data)
            
            return {
                "status": "success",
                "message": f"Models retrained with {len(training_data)} samples",
                "accuracy": self.ml_model_metadata.get("intent_accuracy", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def analyze_text(self, text: str, context: str = "", user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Comprehensive text analysis with smart sentiment and severity assessment.
        This is the main pipeline integration point for all text analysis.
        """
        try:
            start_time = datetime.utcnow()
            
            # Step 1: Basic text preprocessing
            processed_text = self._preprocess_text(text)
            
            # Step 2: Language detection
            language_info = self.detect_language(processed_text)
            
            # Step 3: Sentiment analysis (multiple methods)
            sentiment_analysis = self._comprehensive_sentiment_analysis(processed_text, language_info)
            
            # Step 4: Severity assessment
            severity_analysis = self._assess_severity(processed_text, sentiment_analysis, context)
            
            # Step 5: Emotion detection
            emotion_analysis = self._detect_emotions(processed_text, language_info)
            
            # Step 6: Toxicity and abuse detection
            toxicity_analysis = self._analyze_toxicity_and_abuse(processed_text, sentiment_analysis)
            
            # Step 7: Intent classification
            intent_analysis = self.classify_intent_and_extract_details(processed_text, context)
            
            # Step 8: Risk assessment
            risk_assessment = self._assess_risk_level(processed_text, sentiment_analysis, severity_analysis, toxicity_analysis)
            
            # Step 9: Generate insights and recommendations
            insights = self._generate_insights_and_recommendations(
                processed_text, sentiment_analysis, severity_analysis, 
                emotion_analysis, toxicity_analysis, intent_analysis, risk_assessment
            )
            
            # Step 10: Store analysis for learning
            self._store_analysis_for_learning(
                text, processed_text, sentiment_analysis, severity_analysis, 
                emotion_analysis, toxicity_analysis, intent_analysis, 
                risk_assessment, user_id, context
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "text_analysis": {
                    "original_text": text,
                    "processed_text": processed_text,
                    "language": language_info,
                    "processing_time": processing_time
                },
                "sentiment_analysis": sentiment_analysis,
                "severity_analysis": severity_analysis,
                "emotion_analysis": emotion_analysis,
                "toxicity_analysis": toxicity_analysis,
                "intent_analysis": intent_analysis,
                "risk_assessment": risk_assessment,
                "insights": insights,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "context": context,
                    "analysis_version": "2.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive text analysis: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_fallback_analysis(text, str(e))

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\-\'\"]', '', text)
            
            # Normalize quotes and apostrophes
            text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
            
            return text
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return text

    def _comprehensive_sentiment_analysis(self, text: str, language_info: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive sentiment analysis using multiple methods"""
        try:
            # Method 1: Google Cloud Natural Language API
            google_sentiment = self.analyze_sentiment_and_toxicity(text)
            
            # Method 2: OpenAI-based sentiment analysis
            openai_sentiment = self._analyze_sentiment_with_openai(text, language_info)
            
            # Method 3: Rule-based sentiment analysis
            rule_based_sentiment = self._analyze_sentiment_rules(text)
            
            # Method 4: ML-based sentiment analysis
            ml_sentiment = self._analyze_sentiment_ml(text)
            
            # Combine results with weighted averaging
            combined_sentiment = self._combine_sentiment_results(
                google_sentiment, openai_sentiment, rule_based_sentiment, ml_sentiment
            )
            
            return {
                "google_sentiment": google_sentiment,
                "openai_sentiment": openai_sentiment,
                "rule_based_sentiment": rule_based_sentiment,
                "ml_sentiment": ml_sentiment,
                "combined_sentiment": combined_sentiment,
                "confidence": self._calculate_sentiment_confidence(
                    google_sentiment, openai_sentiment, rule_based_sentiment, ml_sentiment
                )
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive sentiment analysis: {e}")
            return {
                "google_sentiment": {"sentiment_score": 0.0, "sentiment_magnitude": 0.0},
                "openai_sentiment": {"sentiment_score": 0.0, "confidence": 0.0},
                "rule_based_sentiment": {"sentiment_score": 0.0, "polarity": "neutral"},
                "ml_sentiment": {"sentiment_score": 0.0, "confidence": 0.0},
                "combined_sentiment": {"sentiment_score": 0.0, "sentiment_label": "neutral"},
                "confidence": 0.0
            }

    def _analyze_sentiment_with_openai(self, text: str, language_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI"""
        try:
            if not self.has_openai_key:
                return {"sentiment_score": 0.0, "confidence": 0.0, "method": "fallback"}
            
            system_prompt = f"""
                You are an expert sentiment analysis system. Analyze the sentiment of the given text.
                Language: {language_info.get('language_name', 'English')}
                
                Return a JSON object with:
                - "sentiment_score": A number between -1 (very negative) and 1 (very positive)
                - "sentiment_label": One of: very_negative, negative, neutral, positive, very_positive
                - "confidence": A number between 0 and 1 indicating confidence in the analysis
                - "reasoning": Brief explanation of the sentiment classification
            """
            
            user_prompt = f"Analyze the sentiment of this text: '{text}'"
            
            response = self._get_chat_completion(system_prompt, user_prompt)
            
            try:
                # Clean response and parse JSON
                if response.startswith("```json"):
                    response = response[7:-4].strip()
                elif response.startswith("```"):
                    response = response[3:-3].strip()
                
                result = json.loads(response)
                return {
                    "sentiment_score": result.get("sentiment_score", 0.0),
                    "sentiment_label": result.get("sentiment_label", "neutral"),
                    "confidence": result.get("confidence", 0.0),
                    "reasoning": result.get("reasoning", ""),
                    "method": "openai"
                }
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_sentiment_from_text(response)
                
        except Exception as e:
            logger.error(f"Error in OpenAI sentiment analysis: {e}")
            return {"sentiment_score": 0.0, "confidence": 0.0, "method": "error"}

    def _analyze_sentiment_rules(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis"""
        try:
            # Positive words and phrases
            positive_patterns = [
                r'\b(good|great|excellent|amazing|wonderful|fantastic|perfect|awesome|outstanding|superb)\b',
                r'\b(happy|pleased|satisfied|content|delighted|thrilled|excited|joyful)\b',
                r'\b(thank|thanks|appreciate|grateful|blessed|fortunate)\b',
                r'\b(love|like|enjoy|adore|cherish|treasure)\b',
                r'\b(helpful|useful|beneficial|valuable|worthwhile|productive)\b'
            ]
            
            # Negative words and phrases
            negative_patterns = [
                r'\b(bad|terrible|awful|horrible|dreadful|atrocious|abysmal|appalling)\b',
                r'\b(angry|furious|mad|irritated|annoyed|frustrated|upset|disappointed)\b',
                r'\b(hate|dislike|loathe|despise|abhor|detest)\b',
                r'\b(useless|worthless|pointless|meaningless|futile|hopeless)\b',
                r'\b(pain|suffering|agony|misery|distress|anguish)\b'
            ]
            
            # Intensifiers
            intensifiers = [
                r'\b(very|extremely|absolutely|completely|totally|utterly|entirely)\b',
                r'\b(really|truly|genuinely|sincerely|honestly)\b'
            ]
            
            text_lower = text.lower()
            
            # Count positive and negative matches
            positive_count = sum(len(re.findall(pattern, text_lower)) for pattern in positive_patterns)
            negative_count = sum(len(re.findall(pattern, text_lower)) for pattern in negative_patterns)
            intensifier_count = sum(len(re.findall(pattern, text_lower)) for pattern in intensifiers)
            
            # Calculate sentiment score
            total_words = len(text.split())
            if total_words == 0:
                return {"sentiment_score": 0.0, "polarity": "neutral", "method": "rules"}
            
            # Base sentiment
            if positive_count > negative_count:
                base_score = positive_count / total_words
            elif negative_count > positive_count:
                base_score = -negative_count / total_words
            else:
                base_score = 0.0
            
            # Apply intensifier multiplier
            intensifier_multiplier = 1.0 + (intensifier_count * 0.2)
            final_score = max(-1.0, min(1.0, base_score * intensifier_multiplier))
            
            # Determine polarity
            if final_score >= 0.1:
                polarity = "positive"
            elif final_score <= -0.1:
                polarity = "negative"
            else:
                polarity = "neutral"
            
            return {
                "sentiment_score": final_score,
                "polarity": polarity,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "intensifier_count": intensifier_count,
                "method": "rules"
            }
            
        except Exception as e:
            logger.error(f"Error in rule-based sentiment analysis: {e}")
            return {"sentiment_score": 0.0, "polarity": "neutral", "method": "error"}

    def _analyze_sentiment_ml(self, text: str) -> Dict[str, Any]:
        """ML-based sentiment analysis"""
        try:
            # Use existing ML models for sentiment prediction
            if not self.ml_models or "tfidf" not in self.vectorizers:
                return {"sentiment_score": 0.0, "confidence": 0.0, "method": "fallback"}
            
            # Vectorize text
            X = self.vectorizers["tfidf"].transform([text])
            
            # For now, use a simple heuristic based on the text features
            # In production, you'd have a dedicated sentiment classifier
            features = X.toarray()[0]
            
            # Simple sentiment score based on feature weights
            sentiment_score = np.sum(features) / len(features) if len(features) > 0 else 0.0
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            # Confidence based on feature density
            confidence = min(1.0, np.sum(features > 0) / len(features) if len(features) > 0 else 0.0)
            
            return {
                "sentiment_score": float(sentiment_score),
                "confidence": float(confidence),
                "method": "ml"
            }
            
        except Exception as e:
            logger.error(f"Error in ML sentiment analysis: {e}")
            return {"sentiment_score": 0.0, "confidence": 0.0, "method": "error"}

    def _combine_sentiment_results(self, google_sentiment: Dict, openai_sentiment: Dict, 
                                 rule_sentiment: Dict, ml_sentiment: Dict) -> Dict[str, Any]:
        """Combine sentiment results from multiple methods"""
        try:
            # Weighted average of sentiment scores
            scores = []
            weights = []
            
            # Google sentiment (highest weight)
            if google_sentiment.get("sentiment_score") is not None:
                scores.append(google_sentiment["sentiment_score"])
                weights.append(0.4)
            
            # OpenAI sentiment
            if openai_sentiment.get("sentiment_score") is not None:
                scores.append(openai_sentiment["sentiment_score"])
                weights.append(0.3)
            
            # Rule-based sentiment
            if rule_sentiment.get("sentiment_score") is not None:
                scores.append(rule_sentiment["sentiment_score"])
                weights.append(0.2)
            
            # ML sentiment
            if ml_sentiment.get("sentiment_score") is not None:
                scores.append(ml_sentiment["sentiment_score"])
                weights.append(0.1)
            
            if not scores:
                return {"sentiment_score": 0.0, "sentiment_label": "neutral"}
            
            # Calculate weighted average
            total_weight = sum(weights)
            if total_weight == 0:
                return {"sentiment_score": 0.0, "sentiment_label": "neutral"}
            
            combined_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            combined_score = max(-1.0, min(1.0, combined_score))
            
            # Determine sentiment label
            if combined_score >= 0.3:
                sentiment_label = "positive"
            elif combined_score <= -0.3:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return {
                "sentiment_score": combined_score,
                "sentiment_label": sentiment_label,
                "method": "weighted_combination"
            }
            
        except Exception as e:
            logger.error(f"Error combining sentiment results: {e}")
            return {"sentiment_score": 0.0, "sentiment_label": "neutral", "method": "error"}

    def _assess_severity(self, text: str, sentiment_analysis: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Assess the severity of the issue based on text analysis"""
        try:
            # Extract sentiment score
            sentiment_score = sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0)
            
            # Severity indicators
            severity_indicators = {
                "critical": [
                    r'\b(emergency|urgent|critical|immediate|asap|right now)\b',
                    r'\b(dangerous|hazardous|unsafe|risky|life-threatening)\b',
                    r'\b(legal|lawyer|attorney|sue|lawsuit|court)\b',
                    r'\b(ceo|president|executive|management|escalate)\b',
                    r'\b(media|press|journalist|reporter|news|social media)\b'
                ],
                "high": [
                    r'\b(very angry|extremely upset|furious|livid|outraged)\b',
                    r'\b(unacceptable|intolerable|unbearable|insufferable)\b',
                    r'\b(never|ever again|boycott|cancel|terminate)\b',
                    r'\b(complaint|formal complaint|official complaint)\b'
                ],
                    "medium": [
                    r'\b(disappointed|frustrated|annoyed|bothered)\b',
                    r'\b(problem|issue|concern|matter)\b',
                    r'\b(help|assist|support|resolve)\b'
                ],
                "low": [
                    r'\b(suggestion|feedback|improvement|enhancement)\b',
                    r'\b(question|inquiry|information|details)\b',
                    r'\b(thank|appreciate|grateful|satisfied)\b'
                ]
            }
            
            text_lower = text.lower()
            severity_scores = {}
            
            # Calculate severity scores for each level
            for level, patterns in severity_indicators.items():
                score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                severity_scores[level] = score
            
            # Determine primary severity level
            max_score = max(severity_scores.values())
            primary_severity = "low"  # default
            
            if max_score > 0:
                for level in ["critical", "high", "medium", "low"]:
                    if severity_scores[level] == max_score:
                        primary_severity = level
                        break
            
            # Adjust severity based on sentiment
            if sentiment_score < -0.5 and primary_severity == "low":
                primary_severity = "medium"
            elif sentiment_score < -0.8 and primary_severity in ["low", "medium"]:
                primary_severity = "high"
            
            # Calculate confidence
            total_indicators = sum(severity_scores.values())
            confidence = min(1.0, total_indicators / 10.0) if total_indicators > 0 else 0.5
            
            return {
                "primary_severity": primary_severity,
                "severity_scores": severity_scores,
                "confidence": confidence,
                "sentiment_influence": abs(sentiment_score),
                "context_factors": self._extract_context_factors(text, context)
            }
            
        except Exception as e:
            logger.error(f"Error assessing severity: {e}")
            return {
                "primary_severity": "medium",
                "severity_scores": {"low": 0, "medium": 1, "high": 0, "critical": 0},
                "confidence": 0.5,
                "sentiment_influence": 0.0,
                "context_factors": []
            }

    def _detect_emotions(self, text: str, language_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect emotions in the text"""
        try:
            # Emotion patterns
            emotion_patterns = {
                "anger": [
                    r'\b(angry|furious|livid|irate|enraged|outraged|mad|fuming)\b',
                    r'\b(rage|wrath|temper|outburst|explosion)\b'
                ],
                "frustration": [
                    r'\b(frustrated|annoyed|irritated|bothered|aggravated)\b',
                    r'\b(fed up|sick of|tired of|had enough)\b'
                ],
                "sadness": [
                    r'\b(sad|depressed|upset|disappointed|heartbroken|devastated)\b',
                    r'\b(crying|tears|sorrow|grief|melancholy)\b'
                ],
                "fear": [
                    r'\b(scared|afraid|frightened|terrified|panicked|worried)\b',
                    r'\b(anxiety|stress|nervous|concerned|apprehensive)\b'
                ],
                "joy": [
                    r'\b(happy|joyful|delighted|thrilled|excited|elated)\b',
                    r'\b(pleased|satisfied|content|grateful|blessed)\b'
                ],
                "surprise": [
                    r'\b(surprised|shocked|amazed|astonished|stunned)\b',
                    r'\b(unexpected|unbelievable|incredible|wow)\b'
                ],
                "disgust": [
                    r'\b(disgusted|revolted|appalled|sickened|repulsed)\b',
                    r'\b(gross|nasty|vile|repulsive|offensive)\b'
                ]
            }
            
            text_lower = text.lower()
            emotion_scores = {}
            
            # Calculate emotion scores
            for emotion, patterns in emotion_patterns.items():
                score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                emotion_scores[emotion] = score
            
            # Find primary emotion
            max_score = max(emotion_scores.values())
            primary_emotion = "neutral"
            
            if max_score > 0:
                for emotion, score in emotion_scores.items():
                    if score == max_score:
                        primary_emotion = emotion
                        break
            
            # Calculate emotion intensity
            total_emotion_words = sum(emotion_scores.values())
            intensity = min(1.0, total_emotion_words / 5.0) if total_emotion_words > 0 else 0.0
            
            return {
                "primary_emotion": primary_emotion,
                "emotion_scores": emotion_scores,
                "intensity": intensity,
                "emotion_confidence": min(1.0, total_emotion_words / 3.0) if total_emotion_words > 0 else 0.5
            }
            
        except Exception as e:
            logger.error(f"Error detecting emotions: {e}")
            return {
                "primary_emotion": "neutral",
                "emotion_scores": {},
                "intensity": 0.0,
                "emotion_confidence": 0.5
            }

    def _analyze_toxicity_and_abuse(self, text: str, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced toxicity and abuse analysis"""
        try:
            # Get existing toxicity analysis
            toxicity_score = self._calculate_toxicity_score(text)
            
            # Additional abuse patterns
            abuse_patterns = {
                "verbal_abuse": [
                    r'\b(idiot|stupid|dumb|moron|fool|imbecile)\b',
                    r'\b(worthless|useless|pathetic|incompetent)\b'
                ],
                "threats": [
                    r'\b(kill|murder|attack|harm|hurt|destroy)\b',
                    r'\b(sue|legal|court|lawyer|attorney)\b',
                    r'\b(fire|terminate|dismiss|remove)\b'
                ],
                "discrimination": [
                    r'\b(racist|sexist|homophobic|transphobic)\b',
                    r'\b(discriminat|bias|prejudice|stereotype)\b'
                ],
                "harassment": [
                    r'\b(harass|stalk|bully|intimidate|threaten)\b',
                    r'\b(unwanted|unwelcome|inappropriate|offensive)\b'
                ]
            }
            
            text_lower = text.lower()
            abuse_scores = {}
            
            # Calculate abuse scores
            for abuse_type, patterns in abuse_patterns.items():
                score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                abuse_scores[abuse_type] = score
            
            # Overall abuse score
            total_abuse_score = sum(abuse_scores.values()) / len(abuse_scores) if abuse_scores else 0.0
            total_abuse_score = min(1.0, total_abuse_score)
            
            # Combine with toxicity score
            combined_abuse_score = max(toxicity_score, total_abuse_score)
            
            # Determine abuse level
            if combined_abuse_score >= 0.7:
                abuse_level = "high"
            elif combined_abuse_score >= 0.4:
                abuse_level = "medium"
            else:
                abuse_level = "low"
            
            return {
                "toxicity_score": toxicity_score,
                "abuse_scores": abuse_scores,
                "combined_abuse_score": combined_abuse_score,
                "abuse_level": abuse_level,
                "abuse_types": [k for k, v in abuse_scores.items() if v > 0],
                "requires_escalation": combined_abuse_score >= 0.6
            }
            
        except Exception as e:
            logger.error(f"Error analyzing toxicity and abuse: {e}")
            return {
                "toxicity_score": 0.0,
                "abuse_scores": {},
                "combined_abuse_score": 0.0,
                "abuse_level": "low",
                "abuse_types": [],
                "requires_escalation": False
            }

    def _assess_risk_level(self, text: str, sentiment_analysis: Dict[str, Any], 
                          severity_analysis: Dict[str, Any], toxicity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level of the message"""
        try:
            # Risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Sentiment risk
            sentiment_score = sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0)
            if sentiment_score < -0.7:
                risk_factors.append("very_negative_sentiment")
                risk_score += 0.3
            
            # Severity risk
            severity = severity_analysis.get("primary_severity", "low")
            if severity == "critical":
                risk_factors.append("critical_severity")
                risk_score += 0.4
            elif severity == "high":
                risk_factors.append("high_severity")
                risk_score += 0.3
            
            # Toxicity risk
            abuse_score = toxicity_analysis.get("combined_abuse_score", 0.0)
            if abuse_score >= 0.7:
                risk_factors.append("high_abuse")
                risk_score += 0.4
            elif abuse_score >= 0.4:
                risk_factors.append("medium_abuse")
                risk_score += 0.2
            
            # Legal risk indicators
            legal_indicators = [
                r'\b(lawyer|attorney|legal|court|lawsuit|sue|litigation)\b',
                r'\b(ceo|president|executive|management|escalate)\b',
                r'\b(media|press|journalist|reporter|news)\b'
            ]
            
            text_lower = text.lower()
            legal_risk = sum(len(re.findall(pattern, text_lower)) for pattern in legal_indicators)
            if legal_risk > 0:
                risk_factors.append("legal_implications")
                risk_score += 0.3
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "risk_level": risk_level,
                "risk_score": min(1.0, risk_score),
                "risk_factors": risk_factors,
                "requires_immediate_attention": risk_score >= 0.6,
                "escalation_recommended": risk_score >= 0.5
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return {
                "risk_level": "low",
                "risk_score": 0.0,
                "risk_factors": [],
                "requires_immediate_attention": False,
                "escalation_recommended": False
            }

    def _generate_insights_and_recommendations(self, text: str, sentiment_analysis: Dict[str, Any],
                                             severity_analysis: Dict[str, Any], emotion_analysis: Dict[str, Any],
                                             toxicity_analysis: Dict[str, Any], intent_analysis: Dict[str, Any],
                                             risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations based on analysis"""
        try:
            insights = []
            recommendations = []
            
            # Sentiment insights
            sentiment_score = sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0)
            if sentiment_score < -0.5:
                insights.append("User is expressing strong negative sentiment")
                recommendations.append("Consider empathetic response and immediate attention")
            
            # Severity insights
            severity = severity_analysis.get("primary_severity", "low")
            if severity in ["critical", "high"]:
                insights.append(f"High severity issue detected: {severity}")
                recommendations.append("Prioritize for immediate resolution")
            
            # Emotion insights
            primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
            if primary_emotion in ["anger", "frustration"]:
                insights.append(f"User is experiencing {primary_emotion}")
                recommendations.append("Use calming and de-escalation techniques")
            
            # Toxicity insights
            abuse_level = toxicity_analysis.get("abuse_level", "low")
            if abuse_level in ["medium", "high"]:
                insights.append(f"Abuse detected: {abuse_level} level")
                recommendations.append("Maintain professional tone, consider escalation")
            
            # Risk insights
            risk_level = risk_assessment.get("risk_level", "low")
            if risk_level in ["medium", "high"]:
                insights.append(f"High risk situation: {risk_level} risk level")
                recommendations.append("Escalate to senior support or management")
            
            # Response recommendations
            response_priority = "normal"
            if risk_assessment.get("requires_immediate_attention"):
                response_priority = "urgent"
            elif severity in ["critical", "high"]:
                response_priority = "high"
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "response_priority": response_priority,
                "suggested_response_tone": self._suggest_response_tone(sentiment_analysis, emotion_analysis, toxicity_analysis),
                "escalation_needed": risk_assessment.get("escalation_recommended", False)
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "insights": ["Analysis completed"],
                "recommendations": ["Standard response recommended"],
                "response_priority": "normal",
                "suggested_response_tone": "professional",
                "escalation_needed": False
            }

    def _suggest_response_tone(self, sentiment_analysis: Dict[str, Any], 
                             emotion_analysis: Dict[str, Any], 
                             toxicity_analysis: Dict[str, Any]) -> str:
        """Suggest appropriate response tone"""
        try:
            # Check for high abuse
            if toxicity_analysis.get("abuse_level") in ["medium", "high"]:
                return "firm_professional"
            
            # Check for strong emotions
            primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
            if primary_emotion in ["anger", "frustration"]:
                return "calming_empathetic"
            
            # Check sentiment
            sentiment_score = sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0)
            if sentiment_score < -0.5:
                return "empathetic_supportive"
            elif sentiment_score > 0.3:
                return "positive_encouraging"
            else:
                return "professional_helpful"
                
        except Exception as e:
            logger.error(f"Error suggesting response tone: {e}")
            return "professional"

    def _extract_context_factors(self, text: str, context: str) -> List[str]:
        """Extract context factors from text and context"""
        try:
            factors = []
            
            # Time-based factors
            time_patterns = [
                r'\b(yesterday|today|tomorrow|morning|afternoon|evening|night)\b',
                r'\b(urgent|immediate|asap|right now|soon)\b'
            ]
            
            # Location-based factors
            location_patterns = [
                r'\b(store|branch|location|office|headquarters)\b',
                r'\b(online|website|app|mobile|phone)\b'
            ]
            
            # Product/service factors
            product_patterns = [
                r'\b(product|service|order|purchase|item)\b',
                r'\b(delivery|shipping|return|refund|exchange)\b'
            ]
            
            text_lower = text.lower()
            
            for pattern in time_patterns:
                if re.search(pattern, text_lower):
                    factors.append("time_sensitive")
                    break
            
            for pattern in location_patterns:
                if re.search(pattern, text_lower):
                    factors.append("location_specific")
                    break
            
            for pattern in product_patterns:
                if re.search(pattern, text_lower):
                    factors.append("product_service_related")
                    break
            
            return factors
            
        except Exception as e:
            logger.error(f"Error extracting context factors: {e}")
            return []

    def _store_analysis_for_learning(self, original_text: str, processed_text: str,
                                   sentiment_analysis: Dict[str, Any], severity_analysis: Dict[str, Any],
                                   emotion_analysis: Dict[str, Any], toxicity_analysis: Dict[str, Any],
                                   intent_analysis: Dict[str, Any], risk_assessment: Dict[str, Any],
                                   user_id: Optional[int], context: str):
        """Store analysis results for learning and improvement"""
        try:
            # Create analysis record
            analysis_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "original_text": original_text,
                "processed_text": processed_text,
                "sentiment_score": sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0),
                "severity": severity_analysis.get("primary_severity", "low"),
                "emotion": emotion_analysis.get("primary_emotion", "neutral"),
                "toxicity_score": toxicity_analysis.get("combined_abuse_score", 0.0),
                "risk_level": risk_assessment.get("risk_level", "low"),
                "user_id": user_id,
                "context": context
            }
            
            # Store in learning cache
            if "analysis_history" not in self.learning_cache:
                self.learning_cache["analysis_history"] = []
            
            self.learning_cache["analysis_history"].append(analysis_record)
            
            # Keep only last 1000 records
            if len(self.learning_cache["analysis_history"]) > 1000:
                self.learning_cache["analysis_history"] = self.learning_cache["analysis_history"][-1000:]
            
            logger.info(f"Stored analysis for learning: {analysis_record['timestamp']}")
            
        except Exception as e:
            logger.error(f"Error storing analysis for learning: {e}")

    def _get_fallback_analysis(self, text: str, error: str) -> Dict[str, Any]:
        """Get fallback analysis when main analysis fails"""
        return {
            "text_analysis": {
                "original_text": text,
                "processed_text": text,
                "language": {"language_code": "en", "language_name": "English", "confidence": 1.0, "method": "fallback"},
                "processing_time": 0.0
            },
            "sentiment_analysis": {
                "combined_sentiment": {"sentiment_score": 0.0, "sentiment_label": "neutral"},
                "confidence": 0.0
            },
            "severity_analysis": {
                "primary_severity": "low",
                "confidence": 0.5
            },
            "emotion_analysis": {
                "primary_emotion": "neutral",
                "intensity": 0.0
            },
            "toxicity_analysis": {
                "toxicity_score": 0.0,
                "abuse_level": "low"
            },
            "intent_analysis": {
                "category": "complaint",
                "urgency": "medium"
            },
            "risk_assessment": {
                "risk_level": "low",
                "risk_score": 0.0
            },
            "insights": ["Analysis failed, using fallback"],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "error": error,
                "analysis_version": "2.0"
            }
        }

    def _calculate_sentiment_confidence(self, google_sentiment: Dict, openai_sentiment: Dict,
                                      rule_sentiment: Dict, ml_sentiment: Dict) -> float:
        """Calculate confidence in sentiment analysis"""
        try:
            confidences = []
            
            # Google sentiment confidence
            if google_sentiment.get("sentiment_magnitude"):
                confidences.append(min(1.0, google_sentiment["sentiment_magnitude"]))
            
            # OpenAI sentiment confidence
            if openai_sentiment.get("confidence"):
                confidences.append(openai_sentiment["confidence"])
            
            # ML sentiment confidence
            if ml_sentiment.get("confidence"):
                confidences.append(ml_sentiment["confidence"])
            
            # Rule-based confidence (based on pattern matches)
            if rule_sentiment.get("positive_count") or rule_sentiment.get("negative_count"):
                total_patterns = (rule_sentiment.get("positive_count", 0) + 
                                rule_sentiment.get("negative_count", 0))
                rule_confidence = min(1.0, total_patterns / 5.0)
                confidences.append(rule_confidence)
            
            return sum(confidences) / len(confidences) if confidences else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating sentiment confidence: {e}")
            return 0.5

    def _parse_sentiment_from_text(self, text: str) -> Dict[str, Any]:
        """Parse sentiment from OpenAI text response"""
        try:
            text_lower = text.lower()
            
            # Extract sentiment score
            score_match = re.search(r'sentiment_score["\s]*:["\s]*([-\d.]+)', text_lower)
            sentiment_score = float(score_match.group(1)) if score_match else 0.0
            
            # Extract confidence
            conf_match = re.search(r'confidence["\s]*:["\s]*([\d.]+)', text_lower)
            confidence = float(conf_match.group(1)) if conf_match else 0.5
            
            # Extract sentiment label
            label_match = re.search(r'sentiment_label["\s]*:["\s]*["\s]*([a-z_]+)', text_lower)
            sentiment_label = label_match.group(1) if label_match else "neutral"
            
            return {
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "confidence": confidence,
                "method": "openai_parsed"
            }
            
        except Exception as e:
            logger.error(f"Error parsing sentiment from text: {e}")
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.5,
                "method": "fallback"
            }

    def analyze_text_with_context(self, text: str, context: str = "", brand_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze text with conversation context for enhanced understanding.
        This method provides context-aware analysis for conversation management.
        """
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Detect language
            language_info = self.detect_language(processed_text)
            
            # Basic intent classification
            intent_analysis = self.classify_intent_and_extract_details(processed_text)
            
            # Enhanced sentiment analysis with context
            sentiment_analysis = self._comprehensive_sentiment_analysis(processed_text, language_info)
            
            # Context-aware severity assessment
            severity_analysis = self._assess_severity_with_context(processed_text, sentiment_analysis, context)
            
            # Emotion detection
            emotion_analysis = self._detect_emotions(processed_text, language_info)
            
            # Toxicity and abuse detection
            toxicity_analysis = self._analyze_toxicity_and_abuse(processed_text, sentiment_analysis)
            
            # Risk assessment
            risk_assessment = self._assess_risk_level(processed_text, sentiment_analysis, severity_analysis, toxicity_analysis)
            
            # Context-aware insights
            insights = self._generate_contextual_insights(processed_text, context, intent_analysis, sentiment_analysis)
            
            # Determine if follow-up is needed
            follow_up_analysis = self._analyze_follow_up_needs(processed_text, context, intent_analysis)
            
            # Combine all analyses
            comprehensive_analysis = {
                "text": text,
                "processed_text": processed_text,
                "language_info": language_info,
                "intent_analysis": intent_analysis,
                "sentiment_analysis": sentiment_analysis,
                "severity_analysis": severity_analysis,
                "emotion_analysis": emotion_analysis,
                "toxicity_analysis": toxicity_analysis,
                "risk_assessment": risk_assessment,
                "context_insights": insights,
                "follow_up_analysis": follow_up_analysis,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "context_used": bool(context.strip()),
                "brand_id": brand_id
            }
            
            # Store for learning if brand_id provided
            if brand_id:
                self._store_contextual_analysis_for_learning(
                    text, processed_text, comprehensive_analysis, context, brand_id
                )
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in context-aware text analysis: {e}")
            return self._get_fallback_contextual_analysis(text, context, str(e))

    def _assess_severity_with_context(self, text: str, sentiment_analysis: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Assess severity with conversation context"""
        try:
            # Get base severity assessment
            base_severity = self._assess_severity(text, sentiment_analysis, context)
            
            # Enhance with context analysis
            context_factors = self._extract_context_factors(text, context)
            
            # Adjust severity based on context
            adjusted_severity = base_severity.copy()
            
            # Check for repeated issues in context
            if "repeated_issue" in context_factors:
                adjusted_severity["level"] = self._escalate_severity(base_severity["level"])
                adjusted_severity["context_factors"].append("repeated_issue")
            
            # Check for escalation patterns
            if "escalation" in context_factors:
                adjusted_severity["level"] = self._escalate_severity(base_severity["level"])
                adjusted_severity["context_factors"].append("escalation")
            
            # Check for unresolved issues
            if "unresolved" in context_factors:
                adjusted_severity["level"] = self._escalate_severity(base_severity["level"])
                adjusted_severity["context_factors"].append("unresolved")
            
            return adjusted_severity
            
        except Exception as e:
            logger.error(f"Error in context-aware severity assessment: {e}")
            return self._assess_severity(text, sentiment_analysis, context)

    def _escalate_severity(self, current_level: str) -> str:
        """Escalate severity level based on context"""
        severity_levels = ["low", "medium", "high", "critical"]
        try:
            current_index = severity_levels.index(current_level)
            escalated_index = min(current_index + 1, len(severity_levels) - 1)
            return severity_levels[escalated_index]
        except ValueError:
            return "high"  # Default escalation

    def _generate_contextual_insights(self, text: str, context: str, intent_analysis: Dict[str, Any], 
                                    sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on conversation context"""
        try:
            insights = {
                "is_follow_up": False,
                "responding_to_question": False,
                "provides_new_information": False,
                "repeats_previous_issue": False,
                "shows_escalation": False,
                "context_relevance": 0.0,
                "suggested_actions": []
            }
            
            # Check if this is a follow-up response
            if context:
                context_lower = context.lower()
                text_lower = text.lower()
                
                # Check for question patterns in context
                question_indicators = ["?", "could you", "can you", "please", "tell me"]
                has_question = any(indicator in context_lower for indicator in question_indicators)
                
                if has_question:
                    # Check if response provides information
                    info_indicators = ["yes", "no", "okay", "sure", "here", "it's", "the", "my"]
                    provides_info = any(indicator in text_lower for indicator in info_indicators)
                    
                    insights["is_follow_up"] = True
                    insights["responding_to_question"] = provides_info
                    insights["context_relevance"] = 0.8 if provides_info else 0.3
            
            # Check for escalation patterns
            escalation_keywords = ["again", "still", "not resolved", "unhappy", "angry", "frustrated"]
            if any(keyword in text.lower() for keyword in escalation_keywords):
                insights["shows_escalation"] = True
                insights["suggested_actions"].append("escalate_to_human")
            
            # Check for repeated issues
            if context and intent_analysis.get("category") in context:
                insights["repeats_previous_issue"] = True
                insights["suggested_actions"].append("acknowledge_repetition")
            
            # Check for new information
            entities = intent_analysis.get("entities", {})
            if entities and any(entities.values()):
                insights["provides_new_information"] = True
                insights["suggested_actions"].append("update_context")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating contextual insights: {e}")
            return {"error": str(e)}

    def _analyze_follow_up_needs(self, text: str, context: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if follow-up questions are needed"""
        try:
            follow_up_analysis = {
                "follow_up_required": False,
                "follow_up_type": None,
                "missing_information": [],
                "confidence": 0.0
            }
            
            # Check for missing critical information
            entities = intent_analysis.get("entities", {})
            
            # For complaints, check for order number, product details, etc.
            if intent_analysis.get("category") == "complaint":
                if not entities.get("order_number"):
                    follow_up_analysis["missing_information"].append("order_number")
                
                if not entities.get("product_name"):
                    follow_up_analysis["missing_information"].append("product_details")
                
                if not entities.get("date"):
                    follow_up_analysis["missing_information"].append("incident_date")
            
            # For support requests, check for specific issue details
            elif intent_analysis.get("category") == "support":
                if not entities.get("issue_type"):
                    follow_up_analysis["missing_information"].append("issue_type")
            
            # Determine follow-up type
            if follow_up_analysis["missing_information"]:
                follow_up_analysis["follow_up_required"] = True
                follow_up_analysis["follow_up_type"] = "details"
                follow_up_analysis["confidence"] = 0.8
            
            # Check context for unresolved questions
            if context and "?" in context:
                follow_up_analysis["follow_up_required"] = True
                follow_up_analysis["follow_up_type"] = "clarification"
                follow_up_analysis["confidence"] = 0.9
            
            return follow_up_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing follow-up needs: {e}")
            return {"follow_up_required": False, "error": str(e)}

    def _store_contextual_analysis_for_learning(self, original_text: str, processed_text: str, 
                                              analysis: Dict[str, Any], context: str, brand_id: int):
        """Store contextual analysis for learning"""
        try:
            # This would integrate with the self-learning service
            # For now, just log the contextual analysis
            logger.info(f"Contextual analysis stored for brand {brand_id}: {analysis.get('intent_analysis', {}).get('category')}")
            
        except Exception as e:
            logger.error(f"Error storing contextual analysis: {e}")

    def _get_fallback_contextual_analysis(self, text: str, context: str, error: str) -> Dict[str, Any]:
        """Get fallback analysis when context-aware analysis fails"""
        try:
            return {
                "text": text,
                "processed_text": text,
                "language_info": {"language_code": "en", "confidence": 1.0},
                "intent_analysis": {"category": "general", "confidence": 0.5},
                "sentiment_analysis": {"sentiment": "neutral", "score": 0.0},
                "severity_analysis": {"level": "medium", "confidence": 0.5},
                "emotion_analysis": {"primary_emotion": "neutral", "confidence": 0.5},
                "toxicity_analysis": {"is_toxic": False, "score": 0.0},
                "risk_assessment": {"risk_level": "low", "confidence": 0.5},
                "context_insights": {"context_relevance": 0.0},
                "follow_up_analysis": {"follow_up_required": False},
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "context_used": bool(context.strip()),
                "error": error
            }
            
        except Exception as e:
            logger.error(f"Error in fallback contextual analysis: {e}")
            return {"error": str(e)}