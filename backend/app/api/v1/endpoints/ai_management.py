# backend/app/api/v1/endpoints/ai_management.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.api.v1 import deps
from app.core.ai_engine import AIEngine
from app.services.ml_training import MLTrainingService
from app.core.conversation_manager import ConversationManager
from app import crud, schemas
from app.models import BrandKnowledge, AIResponseTemplate, ConversationPattern, AILearningData, ModelTrainingRecord

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
def get_ai_status(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get AI system status"""
    try:
        ai_engine = AIEngine()
        
        return {
            "status": "operational",
            "openai_available": ai_engine.has_openai_key,
            "google_available": ai_engine.has_google_key,
            "ml_models_loaded": len(ai_engine.ml_models),
            "supported_languages": len(ai_engine.supported_languages),
            "ml_model_metadata": ai_engine.ml_model_metadata,
            "learning_cache_size": len(ai_engine.learning_cache)
        }
        
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
def train_models(
    background_tasks: BackgroundTasks,
    brand_id: Optional[int] = None,
    force: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Schedule model training"""
    try:
        ml_service = MLTrainingService(db)
        
        # Check if user has permission for brand-specific training
        if brand_id and current_user.get("role") != "admin":
            # Check if user belongs to the brand
            if current_user.get("brand_id") != brand_id:
                raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        result = ml_service.schedule_retraining(brand_id=brand_id, force=force)
        
        return result
        
    except Exception as e:
        logger.error(f"Error scheduling model training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-history")
def get_training_history(
    model_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get model training history"""
    try:
        query = db.query(ModelTrainingRecord)
        
        if model_type:
            query = query.filter(ModelTrainingRecord.model_type == model_type)
        
        records = query.order_by(ModelTrainingRecord.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "model_type": record.model_type,
                "training_samples": record.training_samples,
                "accuracy_score": record.accuracy_score,
                "precision_score": record.precision_score,
                "recall_score": record.recall_score,
                "f1_score": record.f1_score,
                "training_duration": record.training_duration,
                "model_version": record.model_version,
                "created_at": record.created_at.isoformat(),
                "is_active": record.is_active
            }
            for record in records
        ]
        
    except Exception as e:
        logger.error(f"Error getting training history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/insights")
def get_brand_ai_insights(
    brand_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get brand-specific AI insights"""
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        # Get brand learning insights
        learning_insights = conversation_manager.get_brand_learning_insights(brand_id)
        
        # Get conversation patterns
        patterns = db.query(ConversationPattern).filter(
            ConversationPattern.brand_id == brand_id,
            ConversationPattern.is_active == True
        ).order_by(ConversationPattern.frequency.desc()).limit(20).all()
        
        # Get brand knowledge
        knowledge = db.query(BrandKnowledge).filter(
            BrandKnowledge.brand_id == brand_id,
            BrandKnowledge.is_active == True
        ).all()
        
        # Get recent AI learning data
        recent_learning = db.query(AILearningData).filter(
            AILearningData.brand_id == brand_id,
            AILearningData.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "learning_insights": learning_insights,
            "conversation_patterns": [
                {
                    "id": pattern.id,
                    "type": pattern.pattern_type,
                    "text": pattern.pattern_text,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate,
                    "category": pattern.category,
                    "urgency": pattern.urgency,
                    "language": pattern.language,
                    "created_at": pattern.created_at.isoformat()
                }
                for pattern in patterns
            ],
            "knowledge_base": {
                "total_entries": len(knowledge),
                "by_type": {},
                "by_language": {}
            },
            "recent_learning_data": recent_learning
        }
        
    except Exception as e:
        logger.error(f"Error getting brand AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/knowledge")
def add_brand_knowledge(
    brand_id: int,
    knowledge_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Add brand-specific knowledge"""
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        ml_service = MLTrainingService(db)
        result = ml_service.update_brand_knowledge(brand_id, knowledge_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error adding brand knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/knowledge")
def get_brand_knowledge(
    brand_id: int,
    knowledge_type: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get brand-specific knowledge"""
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        query = db.query(BrandKnowledge).filter(BrandKnowledge.brand_id == brand_id)
        
        if knowledge_type:
            query = query.filter(BrandKnowledge.knowledge_type == knowledge_type)
        
        if language:
            query = query.filter(BrandKnowledge.language == language)
        
        knowledge = query.all()
        
        return [
            {
                "id": k.id,
                "type": k.knowledge_type,
                "question": k.question,
                "answer": k.answer,
                "keywords": k.keywords,
                "confidence_score": k.confidence_score,
                "usage_count": k.usage_count,
                "success_rate": k.success_rate,
                "language": k.language,
                "is_active": k.is_active,
                "created_at": k.created_at.isoformat(),
                "updated_at": k.updated_at.isoformat() if k.updated_at else None
            }
            for k in knowledge
        ]
        
    except Exception as e:
        logger.error(f"Error getting brand knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/templates")
def add_response_template(
    brand_id: int,
    template_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Add AI response template"""
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        template = AIResponseTemplate(
            brand_id=brand_id,
            template_name=template_data["template_name"],
            template_text=template_data["template_text"],
            category=template_data.get("category"),
            urgency=template_data.get("urgency"),
            language=template_data.get("language", "en"),
            variables=template_data.get("variables", [])
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "status": "success",
            "message": "Response template added successfully",
            "template_id": template.id
        }
        
    except Exception as e:
        logger.error(f"Error adding response template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/templates")
def get_response_templates(
    brand_id: int,
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get AI response templates"""
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized for this brand")
        
        query = db.query(AIResponseTemplate).filter(AIResponseTemplate.brand_id == brand_id)
        
        if category:
            query = query.filter(AIResponseTemplate.category == category)
        
        if urgency:
            query = query.filter(AIResponseTemplate.urgency == urgency)
        
        if language:
            query = query.filter(AIResponseTemplate.language == language)
        
        templates = query.all()
        
        return [
            {
                "id": t.id,
                "name": t.template_name,
                "text": t.template_text,
                "category": t.category,
                "urgency": t.urgency,
                "language": t.language,
                "variables": t.variables,
                "usage_count": t.usage_count,
                "success_rate": t.success_rate,
                "is_active": t.is_active,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat() if t.updated_at else None
            }
            for t in templates
        ]
        
    except Exception as e:
        logger.error(f"Error getting response templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-text")
def analyze_text(
    text: str,
    brand_id: Optional[int] = None,
    context: str = "",
    user_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Comprehensive text analysis using AI engine with smart sentiment and severity assessment"""
    try:
        ai_engine = AIEngine()
        
        # Get brand context if provided
        brand_context = ""
        if brand_id:
            conversation_manager = ConversationManager(db, ai_engine)
            brand_context = conversation_manager._get_brand_context(brand_id)
        
        # Use the new comprehensive analyze_text method
        analysis = ai_engine.analyze_text(
            text=text,
            context=context or brand_context,
            user_id=user_id or current_user.get("id")
        )
        
        return {
            "success": True,
            "text": text,
            "analysis": analysis,
            "brand_context": brand_context
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment-analysis")
def analyze_sentiment(
    text: str,
    language: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Analyze sentiment using multiple methods"""
    try:
        ai_engine = AIEngine()
        
        # Detect language if not provided
        if not language:
            language_info = ai_engine.detect_language(text)
            language = language_info.get("language_code", "en")
        
        # Get comprehensive sentiment analysis
        analysis = ai_engine.analyze_text(text, context="", user_id=current_user.get("id"))
        
        return {
            "success": True,
            "text": text,
            "language": language,
            "sentiment_analysis": analysis.get("sentiment_analysis", {}),
            "emotion_analysis": analysis.get("emotion_analysis", {}),
            "toxicity_analysis": analysis.get("toxicity_analysis", {})
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/severity-assessment")
def assess_severity(
    text: str,
    context: str = "",
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Assess severity of the issue"""
    try:
        ai_engine = AIEngine()
        
        # Get comprehensive analysis
        analysis = ai_engine.analyze_text(text, context=context, user_id=current_user.get("id"))
        
        return {
            "success": True,
            "text": text,
            "severity_analysis": analysis.get("severity_analysis", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "insights": analysis.get("insights", {})
        }
        
    except Exception as e:
        logger.error(f"Error assessing severity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion-detection")
def detect_emotions(
    text: str,
    language: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Detect emotions in text"""
    try:
        ai_engine = AIEngine()
        
        # Detect language if not provided
        if not language:
            language_info = ai_engine.detect_language(text)
            language = language_info.get("language_code", "en")
        
        # Get comprehensive analysis
        analysis = ai_engine.analyze_text(text, context="", user_id=current_user.get("id"))
        
        return {
            "success": True,
            "text": text,
            "language": language,
            "emotion_analysis": analysis.get("emotion_analysis", {}),
            "sentiment_analysis": analysis.get("sentiment_analysis", {})
        }
        
    except Exception as e:
        logger.error(f"Error detecting emotions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toxicity-analysis")
def analyze_toxicity(
    text: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Analyze toxicity and abuse in text"""
    try:
        ai_engine = AIEngine()
        
        # Get comprehensive analysis
        analysis = ai_engine.analyze_text(text, context="", user_id=current_user.get("id"))
        
        return {
            "success": True,
            "text": text,
            "toxicity_analysis": analysis.get("toxicity_analysis", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "requires_escalation": analysis.get("toxicity_analysis", {}).get("requires_escalation", False)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing toxicity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comprehensive-analysis")
def comprehensive_analysis(
    text: str,
    brand_id: Optional[int] = None,
    context: str = "",
    include_insights: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get comprehensive analysis with all features"""
    try:
        ai_engine = AIEngine()
        
        # Get brand context if provided
        brand_context = ""
        if brand_id:
            conversation_manager = ConversationManager(db, ai_engine)
            brand_context = conversation_manager._get_brand_context(brand_id)
        
        # Get comprehensive analysis
        analysis = ai_engine.analyze_text(
            text=text,
            context=context or brand_context,
            user_id=current_user.get("id")
        )
        
        # Filter response based on include_insights
        response = {
            "success": True,
            "text": text,
            "text_analysis": analysis.get("text_analysis", {}),
            "sentiment_analysis": analysis.get("sentiment_analysis", {}),
            "severity_analysis": analysis.get("severity_analysis", {}),
            "emotion_analysis": analysis.get("emotion_analysis", {}),
            "toxicity_analysis": analysis.get("toxicity_analysis", {}),
            "intent_analysis": analysis.get("intent_analysis", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "brand_context": brand_context
        }
        
        if include_insights:
            response["insights"] = analysis.get("insights", {})
        
        return response
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis-stats")
def get_analysis_stats(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get analysis statistics and insights"""
    try:
        ai_engine = AIEngine()
        
        # Get learning insights
        insights = ai_engine.get_learning_insights()
        
        # Get model metadata
        model_metadata = ai_engine.ml_model_metadata
        
        return {
            "success": True,
            "learning_insights": insights,
            "model_metadata": model_metadata,
            "supported_languages": len(ai_engine.supported_languages),
            "ml_models_loaded": len(ai_engine.ml_models),
            "analysis_history_count": len(ai_engine.learning_cache.get("analysis_history", []))
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-response")
def generate_response(
    conversation_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Generate AI response for conversation"""
    try:
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        conversation_history = conversation_data.get("history", [])
        brand_id = conversation_data.get("brand_id", 1)
        language = conversation_data.get("language", "en")
        context = conversation_data.get("context", "")
        
        # Generate response
        response = ai_engine.generate_follow_up_question(
            conversation_history, 
            context=context,
            language=language
        )
        
        return {
            "response": response,
            "language": language,
            "brand_id": brand_id
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-data")
def get_learning_data(
    brand_id: Optional[int] = None,
    days: int = 30,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get AI learning data"""
    try:
        # Only admins can access learning data
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        query = db.query(AILearningData)
        
        if brand_id:
            query = query.filter(AILearningData.brand_id == brand_id)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AILearningData.created_at >= cutoff_date)
        
        learning_data = query.order_by(AILearningData.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": data.id,
                "brand_id": data.brand_id,
                "ticket_id": data.ticket_id,
                "user_message": data.user_message,
                "ai_prediction": data.ai_prediction,
                "actual_outcome": data.actual_outcome,
                "confidence_score": data.confidence_score,
                "language": data.language,
                "channel": data.channel,
                "created_at": data.created_at.isoformat()
            }
            for data in learning_data
        ]
        
    except Exception as e:
        logger.error(f"Error getting learning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
def retrain_models(
    background_tasks: BackgroundTasks,
    brand_id: Optional[int] = None,
    force: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Manually trigger model retraining"""
    try:
        # Only admins can trigger retraining
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        ml_service = MLTrainingService(db)
        
        # Collect training data
        training_data = ml_service.collect_training_data(brand_id=brand_id, days=30)
        
        if len(training_data) < 50 and not force:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient training data. Need at least 50 samples, have {len(training_data)}"
            )
        
        # Train models
        result = ml_service.train_models(training_data, force=force)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retraining models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post("/detect-language")
def detect_language(
    text: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Detect the language of input text"""
    try:
        ai_engine = AIEngine()
        detection_result = ai_engine.detect_language(text)
        
        return {
            "text": text,
            "detection_result": detection_result
        }
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate-text")
def translate_text(
    text: str,
    target_language: str = "en",
    source_language: str = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Translate text to target language"""
    try:
        ai_engine = AIEngine()
        translation_result = ai_engine.translate_text(text, target_language, source_language)
        
        return {
            "original_text": text,
            "translation_result": translation_result
        }
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-detect-translate")
def auto_detect_and_translate(
    text: str,
    target_language: str = "en",
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Automatically detect language and translate to target language"""
    try:
        ai_engine = AIEngine()
        result = ai_engine.auto_detect_and_translate(text, target_language)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in auto detect and translate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-multilingual")
def process_multilingual_message(
    text: str,
    target_language: str = "en",
    brand_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Process a message in any language: detect, translate, and analyze"""
    try:
        ai_engine = AIEngine()
        
        # Get brand context if provided
        brand_context = ""
        if brand_id:
            conversation_manager = ConversationManager(db, ai_engine)
            brand_context = conversation_manager._get_brand_context(brand_id)
        
        result = ai_engine.process_multilingual_message(text, brand_context, target_language)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing multilingual message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-languages")
def get_supported_languages(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get list of supported languages"""
    try:
        ai_engine = AIEngine()
        languages = ai_engine.get_supported_languages()
        
        return languages
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 