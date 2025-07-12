# backend/app/services/self_learning_service.py

import logging
import json
import hashlib
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import joblib
import threading
import time
import openai
from collections import defaultdict, Counter

from app.models import (
    AILearningData, ConversationPattern, ModelTrainingRecord, 
    BrandKnowledge, AIResponseTemplate, UserInteraction, Brand
)
from app.core.ai_engine import AIEngine
from app.config import settings

logger = logging.getLogger(__name__)

class SelfLearningService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
        self.brand_models_path = "backend/brand_models"
        self.memory_cache = {}
        self.training_lock = threading.Lock()
        
        # Ensure brand models directory exists
        if not os.path.exists(self.brand_models_path):
            os.makedirs(self.brand_models_path)
        
        # Load brand-specific models
        self.load_brand_models()
    
    def load_brand_models(self):
        """Load brand-specific models from disk"""
        try:
            for brand_dir in os.listdir(self.brand_models_path):
                brand_path = os.path.join(self.brand_models_path, brand_dir)
                if os.path.isdir(brand_path):
                    brand_id = int(brand_dir)
                    
                    # Load brand-specific models
                    brand_models = {
                        "intent_classifier": None,
                        "urgency_classifier": None,
                        "sentiment_classifier": None,
                        "vectorizer": None,
                        "knowledge_embeddings": None,
                        "conversation_patterns": None,
                        "response_templates": None
                    }
                    
                    # Load intent classifier
                    intent_path = os.path.join(brand_path, "intent_classifier.pkl")
                    if os.path.exists(intent_path):
                        brand_models["intent_classifier"] = joblib.load(intent_path)
                    
                    # Load urgency classifier
                    urgency_path = os.path.join(brand_path, "urgency_classifier.pkl")
                    if os.path.exists(urgency_path):
                        brand_models["urgency_classifier"] = joblib.load(urgency_path)
                    
                    # Load sentiment classifier
                    sentiment_path = os.path.join(brand_path, "sentiment_classifier.pkl")
                    if os.path.exists(sentiment_path):
                        brand_models["sentiment_classifier"] = joblib.load(sentiment_path)
                    
                    # Load vectorizer
                    vectorizer_path = os.path.join(brand_path, "vectorizer.pkl")
                    if os.path.exists(vectorizer_path):
                        brand_models["vectorizer"] = joblib.load(vectorizer_path)
                    
                    # Load knowledge embeddings
                    embeddings_path = os.path.join(brand_path, "knowledge_embeddings.pkl")
                    if os.path.exists(embeddings_path):
                        brand_models["knowledge_embeddings"] = joblib.load(embeddings_path)
                    
                    # Load conversation patterns
                    patterns_path = os.path.join(brand_path, "conversation_patterns.pkl")
                    if os.path.exists(patterns_path):
                        brand_models["conversation_patterns"] = joblib.load(patterns_path)
                    
                    # Load response templates
                    templates_path = os.path.join(brand_path, "response_templates.pkl")
                    if os.path.exists(templates_path):
                        brand_models["response_templates"] = joblib.load(templates_path)
                    
                    # Store in memory cache
                    self.memory_cache[brand_id] = brand_models
                    
            logger.info(f"Loaded models for {len(self.memory_cache)} brands")
            
        except Exception as e:
            logger.error(f"Error loading brand models: {e}")
    
    def get_brand_memory(self, brand_id: int) -> Dict[str, Any]:
        """Get brand-specific memory and knowledge"""
        try:
            # Get from cache first
            if brand_id in self.memory_cache:
                return self.memory_cache[brand_id]
            
            # Initialize empty memory for new brand
            brand_memory = {
                "intent_classifier": None,
                "urgency_classifier": None,
                "sentiment_classifier": None,
                "vectorizer": None,
                "knowledge_embeddings": None,
                "conversation_patterns": None,
                "response_templates": None,
                "knowledge_base": {},
                "conversation_history": [],
                "user_preferences": {},
                "common_issues": {},
                "resolution_patterns": {},
                "response_effectiveness": {}
            }
            
            # Load from database
            brand_memory.update(self._load_brand_knowledge_from_db(brand_id))
            
            # Cache the memory
            self.memory_cache[brand_id] = brand_memory
            
            return brand_memory
            
        except Exception as e:
            logger.error(f"Error getting brand memory: {e}")
            return {}
    
    def _load_brand_knowledge_from_db(self, brand_id: int) -> Dict[str, Any]:
        """Load brand knowledge from database"""
        try:
            # Get brand knowledge
            knowledge = self.db.query(BrandKnowledge).filter(
                BrandKnowledge.brand_id == brand_id,
                BrandKnowledge.is_active == True
            ).all()
            
            knowledge_base = {}
            for item in knowledge:
                knowledge_base[item.knowledge_type] = {
                    "question": item.question,
                    "answer": item.answer,
                    "keywords": item.keywords or [],
                    "confidence": item.confidence_score,
                    "usage_count": item.usage_count,
                    "success_rate": item.success_rate
                }
            
            # Get conversation patterns
            patterns = self.db.query(ConversationPattern).filter(
                ConversationPattern.brand_id == brand_id,
                ConversationPattern.is_active == True
            ).all()
            
            conversation_patterns = {}
            for pattern in patterns:
                conversation_patterns[pattern.pattern_type] = {
                    "text": pattern.pattern_text,
                    "frequency": pattern.frequency,
                    "category": pattern.category,
                    "urgency": pattern.urgency,
                    "language": pattern.language
                }
            
            # Get response templates
            templates = self.db.query(AIResponseTemplate).filter(
                AIResponseTemplate.brand_id == brand_id,
                AIResponseTemplate.is_active == True
            ).all()
            
            response_templates = {}
            for template in templates:
                response_templates[template.template_name] = {
                    "text": template.template_text,
                    "category": template.category,
                    "urgency": template.urgency,
                    "language": template.language,
                    "success_rate": template.success_rate,
                    "usage_count": template.usage_count
                }
            
            return {
                "knowledge_base": knowledge_base,
                "conversation_patterns": conversation_patterns,
                "response_templates": response_templates
            }
            
        except Exception as e:
            logger.error(f"Error loading brand knowledge from DB: {e}")
            return {}
    
    def store_interaction_for_learning(self, brand_id: int, interaction_data: Dict[str, Any]):
        """Store interaction data for learning"""
        try:
            # Store in database
            learning_data = AILearningData(
                brand_id=brand_id,
                ticket_id=interaction_data.get("ticket_id"),
                user_message=interaction_data["user_message"],
                ai_prediction=interaction_data["ai_prediction"],
                actual_outcome=interaction_data.get("actual_outcome"),
                confidence_score=interaction_data.get("confidence_score", 0.5),
                language=interaction_data.get("language", "en"),
                channel=interaction_data.get("channel", "web")
            )
            
            self.db.add(learning_data)
            self.db.commit()
            
            # Update brand memory
            self._update_brand_memory(brand_id, interaction_data)
            
            # Check if retraining is needed
            self._check_retraining_needed(brand_id)
            
            logger.info(f"Stored interaction for brand {brand_id}")
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            self.db.rollback()
    
    def _update_brand_memory(self, brand_id: int, interaction_data: Dict[str, Any]):
        """Update brand-specific memory with new interaction"""
        try:
            brand_memory = self.get_brand_memory(brand_id)
            
            # Update conversation patterns
            user_message = interaction_data["user_message"]
            ai_response = interaction_data.get("ai_response", "")
            
            # Extract patterns from user message
            user_patterns = self._extract_patterns(user_message)
            for pattern in user_patterns:
                if "user_patterns" not in brand_memory:
                    brand_memory["user_patterns"] = {}
                
                if pattern in brand_memory["user_patterns"]:
                    brand_memory["user_patterns"][pattern]["frequency"] += 1
                else:
                    brand_memory["user_patterns"][pattern] = {
                        "frequency": 1,
                        "category": interaction_data["ai_prediction"].get("category"),
                        "urgency": interaction_data["ai_prediction"].get("urgency"),
                        "first_seen": datetime.utcnow().isoformat()
                    }
            
            # Update response effectiveness
            if "response_effectiveness" not in brand_memory:
                brand_memory["response_effectiveness"] = {}
            
            response_hash = hashlib.md5(ai_response.encode()).hexdigest()
            if response_hash in brand_memory["response_effectiveness"]:
                brand_memory["response_effectiveness"][response_hash]["usage_count"] += 1
                if interaction_data.get("user_satisfaction"):
                    brand_memory["response_effectiveness"][response_hash]["success_count"] += 1
            else:
                brand_memory["response_effectiveness"][response_hash] = {
                    "response": ai_response,
                    "usage_count": 1,
                    "success_count": 1 if interaction_data.get("user_satisfaction") else 0,
                    "category": interaction_data["ai_prediction"].get("category"),
                    "urgency": interaction_data["ai_prediction"].get("urgency")
                }
            
            # Update common issues
            category = interaction_data["ai_prediction"].get("category", "general")
            if "common_issues" not in brand_memory:
                brand_memory["common_issues"] = {}
            
            if category in brand_memory["common_issues"]:
                brand_memory["common_issues"][category]["count"] += 1
            else:
                brand_memory["common_issues"][category] = {
                    "count": 1,
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat()
                }
            
            # Update user preferences
            user_id = interaction_data.get("user_id")
            if user_id:
                if "user_preferences" not in brand_memory:
                    brand_memory["user_preferences"] = {}
                
                if user_id not in brand_memory["user_preferences"]:
                    brand_memory["user_preferences"][user_id] = {
                        "language": interaction_data.get("language", "en"),
                        "preferred_channel": interaction_data.get("channel", "web"),
                        "interaction_count": 0,
                        "common_categories": [],
                        "satisfaction_score": 0.0
                    }
                
                brand_memory["user_preferences"][user_id]["interaction_count"] += 1
                
                # Update common categories
                categories = brand_memory["user_preferences"][user_id]["common_categories"]
                categories.append(category)
                brand_memory["user_preferences"][user_id]["common_categories"] = list(set(categories))
            
            # Update cache
            self.memory_cache[brand_id] = brand_memory
            
        except Exception as e:
            logger.error(f"Error updating brand memory: {e}")
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract conversation patterns from text"""
        try:
            patterns = []
            
            # Extract key phrases (3-5 word combinations)
            words = text.lower().split()
            for i in range(len(words) - 2):
                for j in range(i + 3, min(i + 6, len(words) + 1)):
                    pattern = " ".join(words[i:j])
                    if len(pattern) > 10:  # Minimum pattern length
                        patterns.append(pattern)
            
            # Extract question patterns
            if "?" in text:
                questions = text.split("?")
                for question in questions:
                    if len(question.strip()) > 5:
                        patterns.append(question.strip() + "?")
            
            return patterns[:10]  # Limit to top 10 patterns
            
        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")
            return []
    
    def train_brand_specific_models(self, brand_id: int, force: bool = False) -> Dict[str, Any]:
        """Train brand-specific models"""
        try:
            with self.training_lock:
                if self.is_training and not force:
                    return {"status": "already_training", "message": "Training already in progress"}
                
                self.is_training = True
                
                # Collect brand-specific training data
                training_data = self._collect_brand_training_data(brand_id)
                
                if len(training_data) < 50 and not force:
                    return {
                        "status": "insufficient_data",
                        "message": f"Need at least 50 samples, got {len(training_data)}"
                    }
                
                # Train models
                results = self._train_brand_models(brand_id, training_data)
                
                # Save models
                self._save_brand_models(brand_id, results)
                
                # Update brand memory
                self._update_brand_memory_after_training(brand_id, results)
                
                self.is_training = False
                
                return {
                    "status": "success",
                    "message": f"Trained models with {len(training_data)} samples",
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"Error training brand models: {e}")
            self.is_training = False
            return {"status": "error", "message": str(e)}
    
    def _collect_brand_training_data(self, brand_id: int) -> List[Dict[str, Any]]:
        """Collect brand-specific training data"""
        try:
            # Get learning data for this brand
            learning_data = self.db.query(AILearningData).filter(
                AILearningData.brand_id == brand_id,
                AILearningData.actual_outcome.isnot(None)
            ).all()
            
            training_data = []
            for data in learning_data:
                if data.actual_outcome:
                    training_data.append({
                        "text": data.user_message,
                        "intent": data.ai_prediction.get("category", "complaint"),
                        "urgency": data.ai_prediction.get("urgency", "medium"),
                        "sentiment": data.ai_prediction.get("sentiment_score", 0.0),
                        "actual_intent": data.actual_outcome.get("category", "complaint"),
                        "actual_urgency": data.actual_outcome.get("urgency", "medium"),
                        "actual_sentiment": data.actual_outcome.get("sentiment_score", 0.0),
                        "confidence": data.confidence_score or 0.5,
                        "language": data.language,
                        "channel": data.channel,
                        "success": data.actual_outcome.get("resolved", False)
                    })
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return []
    
    def _train_brand_models(self, brand_id: int, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train brand-specific models"""
        try:
            if not training_data:
                return {"error": "No training data available"}
            
            # Prepare data
            texts = [item["text"] for item in training_data]
            intent_labels = [item["actual_intent"] for item in training_data]
            urgency_labels = [item["actual_urgency"] for item in training_data]
            sentiment_labels = [1 if item["actual_sentiment"] > 0 else 0 if item["actual_sentiment"] < 0 else 2 for item in training_data]
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                stop_words='english',
                min_df=2,
                max_df=0.95
            )
            
            # Fit and transform text data
            X = vectorizer.fit_transform(texts)
            
            # Split data
            X_train, X_test, y_intent_train, y_intent_test = train_test_split(
                X, intent_labels, test_size=0.2, random_state=42, stratify=intent_labels
            )
            
            _, _, y_urgency_train, y_urgency_test = train_test_split(
                X, urgency_labels, test_size=0.2, random_state=42, stratify=urgency_labels
            )
            
            _, _, y_sentiment_train, y_sentiment_test = train_test_split(
                X, sentiment_labels, test_size=0.2, random_state=42, stratify=sentiment_labels
            )
            
            # Train intent classifier
            intent_classifier = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            intent_classifier.fit(X_train, y_intent_train)
            intent_accuracy = accuracy_score(y_intent_test, intent_classifier.predict(X_test))
            
            # Train urgency classifier
            urgency_classifier = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            urgency_classifier.fit(X_train, y_urgency_train)
            urgency_accuracy = accuracy_score(y_urgency_test, urgency_classifier.predict(X_test))
            
            # Train sentiment classifier
            sentiment_classifier = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            sentiment_classifier.fit(X_train, y_sentiment_train)
            sentiment_accuracy = accuracy_score(y_sentiment_test, sentiment_classifier.predict(X_test))
            
            # Create knowledge embeddings
            knowledge_embeddings = self._create_knowledge_embeddings(brand_id, vectorizer)
            
            # Create conversation patterns
            conversation_patterns = self._create_conversation_patterns(brand_id)
            
            # Create response templates
            response_templates = self._create_response_templates(brand_id)
            
            return {
                "intent_classifier": intent_classifier,
                "urgency_classifier": urgency_classifier,
                "sentiment_classifier": sentiment_classifier,
                "vectorizer": vectorizer,
                "knowledge_embeddings": knowledge_embeddings,
                "conversation_patterns": conversation_patterns,
                "response_templates": response_templates,
                "metrics": {
                    "intent_accuracy": float(intent_accuracy),
                    "urgency_accuracy": float(urgency_accuracy),
                    "sentiment_accuracy": float(sentiment_accuracy),
                    "training_samples": len(training_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error training brand models: {e}")
            return {"error": str(e)}
    
    def _create_knowledge_embeddings(self, brand_id: int, vectorizer) -> Dict[str, Any]:
        """Create embeddings for brand knowledge"""
        try:
            # Get brand knowledge
            knowledge = self.db.query(BrandKnowledge).filter(
                BrandKnowledge.brand_id == brand_id,
                BrandKnowledge.is_active == True
            ).all()
            
            embeddings = {}
            for item in knowledge:
                # Create embedding for question and answer
                question_text = item.question or ""
                answer_text = item.answer or ""
                combined_text = f"{question_text} {answer_text}".strip()
                
                if combined_text:
                    embedding = vectorizer.transform([combined_text])
                    embeddings[item.id] = {
                        "embedding": embedding,
                        "question": question_text,
                        "answer": answer_text,
                        "keywords": item.keywords or [],
                        "confidence": item.confidence_score
                    }
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating knowledge embeddings: {e}")
            return {}
    
    def _create_conversation_patterns(self, brand_id: int) -> Dict[str, Any]:
        """Create conversation patterns for brand"""
        try:
            # Get conversation patterns from database
            patterns = self.db.query(ConversationPattern).filter(
                ConversationPattern.brand_id == brand_id,
                ConversationPattern.is_active == True
            ).all()
            
            pattern_data = {}
            for pattern in patterns:
                pattern_data[pattern.pattern_hash] = {
                    "text": pattern.pattern_text,
                    "type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "category": pattern.category,
                    "urgency": pattern.urgency,
                    "language": pattern.language
                }
            
            return pattern_data
            
        except Exception as e:
            logger.error(f"Error creating conversation patterns: {e}")
            return {}
    
    def _create_response_templates(self, brand_id: int) -> Dict[str, Any]:
        """Create response templates for brand"""
        try:
            # Get response templates from database
            templates = self.db.query(AIResponseTemplate).filter(
                AIResponseTemplate.brand_id == brand_id,
                AIResponseTemplate.is_active == True
            ).all()
            
            template_data = {}
            for template in templates:
                template_data[template.template_name] = {
                    "text": template.template_text,
                    "category": template.category,
                    "urgency": template.urgency,
                    "language": template.language,
                    "success_rate": template.success_rate,
                    "usage_count": template.usage_count
                }
            
            return template_data
            
        except Exception as e:
            logger.error(f"Error creating response templates: {e}")
            return {}
    
    def _save_brand_models(self, brand_id: int, models: Dict[str, Any]):
        """Save brand-specific models to disk"""
        try:
            brand_path = os.path.join(self.brand_models_path, str(brand_id))
            if not os.path.exists(brand_path):
                os.makedirs(brand_path)
            
            # Save classifiers
            if "intent_classifier" in models:
                joblib.dump(models["intent_classifier"], 
                           os.path.join(brand_path, "intent_classifier.pkl"))
            
            if "urgency_classifier" in models:
                joblib.dump(models["urgency_classifier"], 
                           os.path.join(brand_path, "urgency_classifier.pkl"))
            
            if "sentiment_classifier" in models:
                joblib.dump(models["sentiment_classifier"], 
                           os.path.join(brand_path, "sentiment_classifier.pkl"))
            
            # Save vectorizer
            if "vectorizer" in models:
                joblib.dump(models["vectorizer"], 
                           os.path.join(brand_path, "vectorizer.pkl"))
            
            # Save other components
            if "knowledge_embeddings" in models:
                joblib.dump(models["knowledge_embeddings"], 
                           os.path.join(brand_path, "knowledge_embeddings.pkl"))
            
            if "conversation_patterns" in models:
                joblib.dump(models["conversation_patterns"], 
                           os.path.join(brand_path, "conversation_patterns.pkl"))
            
            if "response_templates" in models:
                joblib.dump(models["response_templates"], 
                           os.path.join(brand_path, "response_templates.pkl"))
            
            # Save metadata
            metadata = {
                "brand_id": brand_id,
                "last_trained": datetime.utcnow().isoformat(),
                "metrics": models.get("metrics", {}),
                "model_version": f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
            with open(os.path.join(brand_path, "metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update memory cache
            self.memory_cache[brand_id] = models
            
            logger.info(f"Saved models for brand {brand_id}")
            
        except Exception as e:
            logger.error(f"Error saving brand models: {e}")
    
    def _update_brand_memory_after_training(self, brand_id: int, models: Dict[str, Any]):
        """Update brand memory after training"""
        try:
            brand_memory = self.get_brand_memory(brand_id)
            
            # Update with new models
            brand_memory.update({
                "intent_classifier": models.get("intent_classifier"),
                "urgency_classifier": models.get("urgency_classifier"),
                "sentiment_classifier": models.get("sentiment_classifier"),
                "vectorizer": models.get("vectorizer"),
                "knowledge_embeddings": models.get("knowledge_embeddings"),
                "conversation_patterns": models.get("conversation_patterns"),
                "response_templates": models.get("response_templates")
            })
            
            # Update cache
            self.memory_cache[brand_id] = brand_memory
            
        except Exception as e:
            logger.error(f"Error updating brand memory after training: {e}")
    
    def _check_retraining_needed(self, brand_id: int):
        """Check if retraining is needed for brand"""
        try:
            # Get recent learning data count
            recent_data = self.db.query(AILearningData).filter(
                AILearningData.brand_id == brand_id,
                AILearningData.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Get last training time
            brand_path = os.path.join(self.brand_models_path, str(brand_id))
            metadata_path = os.path.join(brand_path, "metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    last_trained = datetime.fromisoformat(metadata["last_trained"])
                    days_since_training = (datetime.utcnow() - last_trained).days
            else:
                days_since_training = 999  # Force training if no previous training
            
            # Retrain if:
            # 1. More than 100 new samples in a week, or
            # 2. More than 30 days since last training, or
            # 3. No previous training exists
            if recent_data >= 100 or days_since_training >= 30:
                logger.info(f"Retraining needed for brand {brand_id}: {recent_data} new samples, {days_since_training} days since training")
                self.train_brand_specific_models(brand_id, force=True)
            
        except Exception as e:
            logger.error(f"Error checking retraining needs: {e}")
    
    def predict_with_brand_models(self, brand_id: int, text: str) -> Dict[str, Any]:
        """Make predictions using brand-specific models"""
        try:
            brand_memory = self.get_brand_memory(brand_id)
            
            # Check if brand has trained models
            if not brand_memory.get("vectorizer") or not brand_memory.get("intent_classifier"):
                # Fall back to global models
                return self.ai_engine.predict_with_ml(text)
            
            # Vectorize text
            X = brand_memory["vectorizer"].transform([text])
            
            # Make predictions
            intent_pred = brand_memory["intent_classifier"].predict(X)[0]
            intent_proba = np.max(brand_memory["intent_classifier"].predict_proba(X))
            
            urgency_pred = brand_memory["urgency_classifier"].predict(X)[0]
            urgency_proba = np.max(brand_memory["urgency_classifier"].predict_proba(X))
            
            sentiment_pred = brand_memory["sentiment_classifier"].predict(X)[0]
            sentiment_proba = np.max(brand_memory["sentiment_classifier"].predict_proba(X))
            
            # Find similar knowledge
            similar_knowledge = self._find_similar_knowledge(brand_id, text, brand_memory)
            
            # Find matching patterns
            matching_patterns = self._find_matching_patterns(brand_id, text, brand_memory)
            
            # Find best response template
            best_template = self._find_best_response_template(brand_id, text, brand_memory)
            
            return {
                "intent": intent_pred,
                "urgency": urgency_pred,
                "sentiment": sentiment_pred,
                "intent_confidence": float(intent_proba),
                "urgency_confidence": float(urgency_proba),
                "sentiment_confidence": float(sentiment_proba),
                "overall_confidence": float((intent_proba + urgency_proba + sentiment_proba) / 3),
                "similar_knowledge": similar_knowledge,
                "matching_patterns": matching_patterns,
                "best_template": best_template,
                "model_source": "brand_specific"
            }
            
        except Exception as e:
            logger.error(f"Error predicting with brand models: {e}")
            # Fall back to global models
            return self.ai_engine.predict_with_ml(text)
    
    def _find_similar_knowledge(self, brand_id: int, text: str, brand_memory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar knowledge for the given text"""
        try:
            if not brand_memory.get("knowledge_embeddings") or not brand_memory.get("vectorizer"):
                return []
            
            # Vectorize input text
            text_vector = brand_memory["vectorizer"].transform([text])
            
            similar_knowledge = []
            for knowledge_id, knowledge_data in brand_memory["knowledge_embeddings"].items():
                # Calculate similarity (cosine similarity)
                similarity = np.dot(text_vector.toarray(), knowledge_data["embedding"].toarray().T)[0][0]
                
                if similarity > 0.3:  # Threshold for similarity
                    similar_knowledge.append({
                        "knowledge_id": knowledge_id,
                        "question": knowledge_data["question"],
                        "answer": knowledge_data["answer"],
                        "similarity": float(similarity),
                        "keywords": knowledge_data["keywords"]
                    })
            
            # Sort by similarity
            similar_knowledge.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similar_knowledge[:3]  # Return top 3 matches
            
        except Exception as e:
            logger.error(f"Error finding similar knowledge: {e}")
            return []
    
    def _find_matching_patterns(self, brand_id: int, text: str, brand_memory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching conversation patterns"""
        try:
            if not brand_memory.get("conversation_patterns"):
                return []
            
            matching_patterns = []
            text_lower = text.lower()
            
            for pattern_hash, pattern_data in brand_memory["conversation_patterns"].items():
                pattern_text = pattern_data["text"].lower()
                
                # Simple pattern matching
                if pattern_text in text_lower or text_lower in pattern_text:
                    matching_patterns.append({
                        "pattern_hash": pattern_hash,
                        "text": pattern_data["text"],
                        "type": pattern_data["type"],
                        "frequency": pattern_data["frequency"],
                        "category": pattern_data["category"],
                        "urgency": pattern_data["urgency"]
                    })
            
            # Sort by frequency
            matching_patterns.sort(key=lambda x: x["frequency"], reverse=True)
            
            return matching_patterns[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Error finding matching patterns: {e}")
            return []
    
    def _find_best_response_template(self, brand_id: int, text: str, brand_memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best response template for the given text"""
        try:
            if not brand_memory.get("response_templates"):
                return None
            
            # Analyze text to get category and urgency
            analysis = self.ai_engine.classify_intent_and_extract_details(text)
            category = analysis.get("category", "complaint")
            urgency = analysis.get("urgency", "medium")
            
            best_template = None
            best_score = 0.0
            
            for template_name, template_data in brand_memory["response_templates"].items():
                score = 0.0
                
                # Category match
                if template_data["category"] == category:
                    score += 0.4
                
                # Urgency match
                if template_data["urgency"] == urgency:
                    score += 0.3
                
                # Success rate
                score += template_data["success_rate"] * 0.3
                
                if score > best_score:
                    best_score = score
                    best_template = {
                        "template_name": template_name,
                        "text": template_data["text"],
                        "category": template_data["category"],
                        "urgency": template_data["urgency"],
                        "success_rate": template_data["success_rate"],
                        "score": score
                    }
            
            return best_template if best_score > 0.5 else None
            
        except Exception as e:
            logger.error(f"Error finding best response template: {e}")
            return None
    
    def get_brand_learning_insights(self, brand_id: int) -> Dict[str, Any]:
        """Get learning insights for a brand"""
        try:
            brand_memory = self.get_brand_memory(brand_id)
            
            # Get recent learning data
            recent_data = self.db.query(AILearningData).filter(
                AILearningData.brand_id == brand_id,
                AILearningData.created_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            # Calculate insights
            total_interactions = len(recent_data)
            successful_interactions = sum(1 for data in recent_data if data.actual_outcome and data.actual_outcome.get("resolved", False))
            success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0.0
            
            # Get common categories
            categories = [data.ai_prediction.get("category", "unknown") for data in recent_data]
            category_counts = Counter(categories)
            
            # Get average confidence
            confidences = [data.confidence_score or 0.0 for data in recent_data]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "total_interactions": total_interactions,
                "successful_interactions": successful_interactions,
                "success_rate": success_rate,
                "average_confidence": avg_confidence,
                "common_categories": dict(category_counts.most_common(5)),
                "knowledge_base_size": len(brand_memory.get("knowledge_base", {})),
                "conversation_patterns": len(brand_memory.get("conversation_patterns", {})),
                "response_templates": len(brand_memory.get("response_templates", {})),
                "user_preferences": len(brand_memory.get("user_preferences", {})),
                "common_issues": brand_memory.get("common_issues", {}),
                "model_metrics": brand_memory.get("metrics", {})
            }
            
        except Exception as e:
            logger.error(f"Error getting brand learning insights: {e}")
            return {}
    
    def cleanup_old_data(self, brand_id: int, days: int = 90):
        """Clean up old learning data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old learning data
            old_data = self.db.query(AILearningData).filter(
                AILearningData.brand_id == brand_id,
                AILearningData.created_at < cutoff_date
            ).delete()
            
            # Delete old conversation patterns
            old_patterns = self.db.query(ConversationPattern).filter(
                ConversationPattern.brand_id == brand_id,
                ConversationPattern.updated_at < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Cleaned up {old_data} old learning records and {old_patterns} old patterns for brand {brand_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            self.db.rollback() 