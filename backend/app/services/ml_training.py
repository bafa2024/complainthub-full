# backend/app/services/ml_training.py

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import threading
import time

from app.models import AILearningData, ConversationPattern, ModelTrainingRecord, BrandKnowledge, AIResponseTemplate, UserInteraction
from app.core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

class MLTrainingService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
        self.model_path = "backend/ml_models"
        self.is_training = False
        self.training_lock = threading.Lock()
        
        # Ensure model directory exists
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
    
    def collect_training_data(self, brand_id: Optional[int] = None, days: int = 30) -> List[Dict[str, Any]]:
        """Collect training data from the database"""
        try:
            # Get AI learning data
            query = self.db.query(AILearningData)
            
            if brand_id:
                query = query.filter(AILearningData.brand_id == brand_id)
            
            # Filter by date
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AILearningData.created_at >= cutoff_date)
            
            learning_data = query.all()
            
            training_data = []
            for data in learning_data:
                if data.actual_outcome:  # Only use data with known outcomes
                    training_data.append({
                        "text": data.user_message,
                        "intent": data.ai_prediction.get("category", "complaint"),
                        "urgency": data.ai_prediction.get("urgency", "medium"),
                        "actual_intent": data.actual_outcome.get("category", "complaint"),
                        "actual_urgency": data.actual_outcome.get("urgency", "medium"),
                        "confidence": data.confidence_score or 0.5,
                        "language": data.language,
                        "brand_id": data.brand_id,
                        "channel": data.channel
                    })
            
            logger.info(f"Collected {len(training_data)} training samples")
            return training_data
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return []
    
    def prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        try:
            if not training_data:
                raise ValueError("No training data provided")
            
            # Extract features and labels
            texts = [item["text"] for item in training_data]
            intent_labels = [item["actual_intent"] for item in training_data]
            urgency_labels = [item["actual_urgency"] for item in training_data]
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 3),
                stop_words='english',
                min_df=2,
                max_df=0.95
            )
            
            # Fit and transform text data
            X = vectorizer.fit_transform(texts)
            
            return X, np.array(intent_labels), np.array(urgency_labels), vectorizer
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    def train_models(self, training_data: List[Dict[str, Any]], force: bool = False) -> Dict[str, Any]:
        """Train ML models with collected data"""
        try:
            if self.is_training and not force:
                return {
                    "status": "training_in_progress",
                    "message": "Training already in progress"
                }
            
            if len(training_data) < 50 and not force:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 50 samples, have {len(training_data)}"
                }
            
            with self.training_lock:
                self.is_training = True
                
                start_time = time.time()
                
                # Prepare training data
                X, intent_labels, urgency_labels, vectorizer = self.prepare_training_data(training_data)
                
                # Split data
                X_train, X_test, intent_train, intent_test, urgency_train, urgency_test = train_test_split(
                    X, intent_labels, urgency_labels, test_size=0.2, random_state=42, stratify=intent_labels
                )
                
                # Train intent classifier
                intent_classifier = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
                
                intent_classifier.fit(X_train, intent_train)
                intent_pred = intent_classifier.predict(X_test)
                intent_accuracy = accuracy_score(intent_test, intent_pred)
                intent_precision, intent_recall, intent_f1, _ = precision_recall_fscore_support(
                    intent_test, intent_pred, average='weighted'
                )
                
                # Train urgency classifier
                urgency_classifier = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
                
                urgency_classifier.fit(X_train, urgency_train)
                urgency_pred = urgency_classifier.predict(X_test)
                urgency_accuracy = accuracy_score(urgency_test, urgency_pred)
                urgency_precision, urgency_recall, urgency_f1, _ = precision_recall_fscore_support(
                    urgency_test, urgency_pred, average='weighted'
                )
                
                # Cross-validation scores
                intent_cv_scores = cross_val_score(intent_classifier, X, intent_labels, cv=5)
                urgency_cv_scores = cross_val_score(urgency_classifier, X, urgency_labels, cv=5)
                
                training_duration = time.time() - start_time
                
                # Save models
                model_version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                
                # Save intent classifier
                intent_model_path = os.path.join(self.model_path, f"intent_classifier_{model_version}.pkl")
                joblib.dump(intent_classifier, intent_model_path)
                
                # Save urgency classifier
                urgency_model_path = os.path.join(self.model_path, f"urgency_classifier_{model_version}.pkl")
                joblib.dump(urgency_classifier, urgency_model_path)
                
                # Save vectorizer
                vectorizer_path = os.path.join(self.model_path, f"tfidf_vectorizer_{model_version}.pkl")
                joblib.dump(vectorizer, vectorizer_path)
                
                # Update AI engine models
                self.ai_engine.ml_models["intent_classifier"] = intent_classifier
                self.ai_engine.ml_models["urgency_classifier"] = urgency_classifier
                self.ai_engine.vectorizers["tfidf"] = vectorizer
                
                # Save metadata
                metadata = {
                    "model_version": model_version,
                    "last_trained": datetime.utcnow().isoformat(),
                    "training_samples": len(training_data),
                    "intent_accuracy": float(intent_accuracy),
                    "intent_precision": float(intent_precision),
                    "intent_recall": float(intent_recall),
                    "intent_f1": float(intent_f1),
                    "intent_cv_mean": float(intent_cv_scores.mean()),
                    "intent_cv_std": float(intent_cv_scores.std()),
                    "urgency_accuracy": float(urgency_accuracy),
                    "urgency_precision": float(urgency_precision),
                    "urgency_recall": float(urgency_recall),
                    "urgency_f1": float(urgency_f1),
                    "urgency_cv_mean": float(urgency_cv_scores.mean()),
                    "urgency_cv_std": float(urgency_cv_scores.std()),
                    "training_duration": float(training_duration),
                    "model_paths": {
                        "intent_classifier": intent_model_path,
                        "urgency_classifier": urgency_model_path,
                        "vectorizer": vectorizer_path
                    }
                }
                
                # Save metadata
                metadata_path = os.path.join(self.model_path, f"model_metadata_{model_version}.json")
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Update AI engine metadata
                self.ai_engine.meta_data = metadata
                
                # Save training record to database
                self._save_training_record(metadata, "intent_classifier")
                self._save_training_record(metadata, "urgency_classifier")
                
                # Clean up old models (keep last 5 versions)
                self._cleanup_old_models()
                
                self.is_training = False
                
                logger.info(f"Models trained successfully. Intent accuracy: {intent_accuracy:.3f}, Urgency accuracy: {urgency_accuracy:.3f}")
                
                return {
                    "status": "success",
                    "message": f"Models trained successfully with {len(training_data)} samples",
                    "model_version": model_version,
                    "metrics": {
                        "intent_accuracy": float(intent_accuracy),
                        "urgency_accuracy": float(urgency_accuracy),
                        "training_duration": float(training_duration)
                    }
                }
                
        except Exception as e:
            self.is_training = False
            logger.error(f"Error training models: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _save_training_record(self, metadata: Dict[str, Any], model_type: str):
        """Save training record to database"""
        try:
            record = ModelTrainingRecord(
                model_type=model_type,
                training_samples=metadata["training_samples"],
                accuracy_score=metadata[f"{model_type.split('_')[0]}_accuracy"],
                precision_score=metadata[f"{model_type.split('_')[0]}_precision"],
                recall_score=metadata[f"{model_type.split('_')[0]}_recall"],
                f1_score=metadata[f"{model_type.split('_')[0]}_f1"],
                training_duration=metadata["training_duration"],
                model_version=metadata["model_version"],
                model_path=metadata["model_paths"][model_type],
                parameters={
                    "n_estimators": 200,
                    "max_depth": 20,
                    "min_samples_split": 5,
                    "min_samples_leaf": 2
                }
            )
            
            self.db.add(record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving training record: {e}")
            self.db.rollback()
    
    def _cleanup_old_models(self, keep_versions: int = 5):
        """Clean up old model versions"""
        try:
            # Get all model files
            model_files = []
            for file in os.listdir(self.model_path):
                if file.endswith('.pkl') or file.endswith('.json'):
                    model_files.append(file)
            
            # Group by version
            versions = {}
            for file in model_files:
                if '_' in file:
                    version = file.split('_')[-1].replace('.pkl', '').replace('.json', '')
                    if version not in versions:
                        versions[version] = []
                    versions[version].append(file)
            
            # Sort versions and keep only the latest ones
            sorted_versions = sorted(versions.keys(), reverse=True)
            versions_to_keep = sorted_versions[:keep_versions]
            
            # Remove old versions
            for version in sorted_versions:
                if version not in versions_to_keep:
                    for file in versions[version]:
                        file_path = os.path.join(self.model_path, file)
                        try:
                            os.remove(file_path)
                            logger.info(f"Removed old model file: {file}")
                        except Exception as e:
                            logger.error(f"Error removing old model file {file}: {e}")
                            
        except Exception as e:
            logger.error(f"Error cleaning up old models: {e}")
    
    def analyze_conversation_patterns(self, brand_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """Analyze conversation patterns for learning"""
        try:
            # Get user interactions
            query = self.db.query(UserInteraction)
            
            if brand_id:
                query = query.filter(UserInteraction.brand_id == brand_id)
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(UserInteraction.created_at >= cutoff_date)
            
            interactions = query.all()
            
            patterns = {
                "common_questions": {},
                "response_effectiveness": {},
                "channel_preferences": {},
                "language_distribution": {},
                "satisfaction_trends": {}
            }
            
            for interaction in interactions:
                # Common questions
                if interaction.interaction_type == "message":
                    question_hash = hashlib.md5(interaction.content.encode()).hexdigest()
                    if question_hash not in patterns["common_questions"]:
                        patterns["common_questions"][question_hash] = {
                            "text": interaction.content,
                            "count": 0,
                            "avg_satisfaction": 0,
                            "channels": set()
                        }
                    
                    patterns["common_questions"][question_hash]["count"] += 1
                    patterns["common_questions"][question_hash]["channels"].add(interaction.channel)
                    
                    if interaction.satisfaction_score:
                        current_avg = patterns["common_questions"][question_hash]["avg_satisfaction"]
                        count = patterns["common_questions"][question_hash]["count"]
                        patterns["common_questions"][question_hash]["avg_satisfaction"] = (
                            (current_avg * (count - 1) + interaction.satisfaction_score) / count
                        )
                
                # Channel preferences
                if interaction.channel not in patterns["channel_preferences"]:
                    patterns["channel_preferences"][interaction.channel] = 0
                patterns["channel_preferences"][interaction.channel] += 1
                
                # Language distribution
                if interaction.language not in patterns["language_distribution"]:
                    patterns["language_distribution"][interaction.language] = 0
                patterns["language_distribution"][interaction.language] += 1
                
                # Satisfaction trends
                if interaction.satisfaction_score:
                    date_key = interaction.created_at.strftime("%Y-%m-%d")
                    if date_key not in patterns["satisfaction_trends"]:
                        patterns["satisfaction_trends"][date_key] = []
                    patterns["satisfaction_trends"][date_key].append(interaction.satisfaction_score)
            
            # Convert sets to lists for JSON serialization
            for question_data in patterns["common_questions"].values():
                question_data["channels"] = list(question_data["channels"])
            
            # Calculate average satisfaction per day
            for date_key in patterns["satisfaction_trends"]:
                scores = patterns["satisfaction_trends"][date_key]
                patterns["satisfaction_trends"][date_key] = sum(scores) / len(scores)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {e}")
            return {}
    
    def update_brand_knowledge(self, brand_id: int, knowledge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update brand knowledge base"""
        try:
            knowledge_type = knowledge_data.get("type")
            question = knowledge_data.get("question")
            answer = knowledge_data.get("answer")
            keywords = knowledge_data.get("keywords", [])
            language = knowledge_data.get("language", "en")
            
            # Check if knowledge already exists
            existing = self.db.query(BrandKnowledge).filter(
                BrandKnowledge.brand_id == brand_id,
                BrandKnowledge.knowledge_type == knowledge_type,
                BrandKnowledge.question == question,
                BrandKnowledge.language == language
            ).first()
            
            if existing:
                # Update existing knowledge
                existing.answer = answer
                existing.keywords = keywords
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                
                return {
                    "status": "updated",
                    "message": "Brand knowledge updated successfully",
                    "knowledge_id": existing.id
                }
            else:
                # Create new knowledge
                new_knowledge = BrandKnowledge(
                    brand_id=brand_id,
                    knowledge_type=knowledge_type,
                    question=question,
                    answer=answer,
                    keywords=keywords,
                    language=language
                )
                
                self.db.add(new_knowledge)
                self.db.commit()
                self.db.refresh(new_knowledge)
                
                return {
                    "status": "created",
                    "message": "Brand knowledge created successfully",
                    "knowledge_id": new_knowledge.id
                }
                
        except Exception as e:
            logger.error(f"Error updating brand knowledge: {e}")
            self.db.rollback()
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status and metrics"""
        try:
            # Get latest training records
            latest_intent = self.db.query(ModelTrainingRecord).filter(
                ModelTrainingRecord.model_type == "intent_classifier"
            ).order_by(desc(ModelTrainingRecord.created_at)).first()
            
            latest_urgency = self.db.query(ModelTrainingRecord).filter(
                ModelTrainingRecord.model_type == "urgency_classifier"
            ).order_by(desc(ModelTrainingRecord.created_at)).first()
            
            # Get data statistics
            total_learning_data = self.db.query(AILearningData).count()
            recent_learning_data = self.db.query(AILearningData).filter(
                AILearningData.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                "is_training": self.is_training,
                "total_learning_data": total_learning_data,
                "recent_learning_data": recent_learning_data,
                "latest_intent_model": {
                    "version": latest_intent.model_version if latest_intent else None,
                    "accuracy": latest_intent.accuracy_score if latest_intent else None,
                    "trained_at": latest_intent.created_at.isoformat() if latest_intent else None
                },
                "latest_urgency_model": {
                    "version": latest_urgency.model_version if latest_urgency else None,
                    "accuracy": latest_urgency.accuracy_score if latest_urgency else None,
                    "trained_at": latest_urgency.created_at.isoformat() if latest_urgency else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting training status: {e}")
            return {
                "is_training": self.is_training,
                "error": str(e)
            }
    
    def schedule_retraining(self, brand_id: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """Schedule model retraining"""
        try:
            # Check if enough new data is available
            if not force:
                recent_data = self.db.query(AILearningData).filter(
                    AILearningData.created_at >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                if recent_data < 20:
                    return {
                        "status": "insufficient_data",
                        "message": f"Only {recent_data} new samples in the last week. Need at least 20 for retraining."
                    }
            
            # Collect training data
            training_data = self.collect_training_data(brand_id, days=30)
            
            if len(training_data) < 50 and not force:
                return {
                    "status": "insufficient_data",
                    "message": f"Only {len(training_data)} training samples available. Need at least 50."
                }
            
            # Start training in background thread
            def train_async():
                self.train_models(training_data, force=force)
            
            training_thread = threading.Thread(target=train_async)
            training_thread.daemon = True
            training_thread.start()
            
            return {
                "status": "scheduled",
                "message": f"Retraining scheduled with {len(training_data)} samples",
                "training_samples": len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error scheduling retraining: {e}")
            return {
                "status": "error",
                "message": str(e)
            } 