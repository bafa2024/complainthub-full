# backend/app/api/v1/endpoints/self_learning.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

from app.api.v1.deps import get_db, get_current_user
from app.services.self_learning_service import SelfLearningService
from app.models import Brand, User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/brand/{brand_id}/memory")
def get_brand_memory(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get brand-specific memory and knowledge"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        brand_memory = self_learning_service.get_brand_memory(brand_id)
        
        return {
            "success": True,
            "brand_id": brand_id,
            "memory": {
                "knowledge_base_size": len(brand_memory.get("knowledge_base", {})),
                "conversation_patterns": len(brand_memory.get("conversation_patterns", {})),
                "response_templates": len(brand_memory.get("response_templates", {})),
                "user_preferences": len(brand_memory.get("user_preferences", {})),
                "common_issues": brand_memory.get("common_issues", {}),
                "has_trained_models": bool(brand_memory.get("intent_classifier")),
                "model_metrics": brand_memory.get("metrics", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting brand memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/train")
def train_brand_models(
    brand_id: int,
    force: bool = Query(False, description="Force training even with insufficient data"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train brand-specific models"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        
        if background_tasks:
            # Run training in background
            background_tasks.add_task(
                self_learning_service.train_brand_specific_models,
                brand_id,
                force
            )
            
            return {
                "success": True,
                "message": "Training started in background",
                "brand_id": brand_id
            }
        else:
            # Run training synchronously
            result = self_learning_service.train_brand_specific_models(brand_id, force)
            
            return {
                "success": result["status"] == "success",
                "message": result["message"],
                "brand_id": brand_id,
                "results": result.get("results", {})
            }
        
    except Exception as e:
        logger.error(f"Error training brand models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/predict")
def predict_with_brand_models(
    brand_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Make predictions using brand-specific models"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        prediction = self_learning_service.predict_with_brand_models(brand_id, text)
        
        return {
            "success": True,
            "brand_id": brand_id,
            "text": text,
            "prediction": prediction
        }
        
    except Exception as e:
        logger.error(f"Error predicting with brand models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/insights")
def get_brand_learning_insights(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get learning insights for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        insights = self_learning_service.get_brand_learning_insights(brand_id)
        
        return {
            "success": True,
            "brand_id": brand_id,
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting brand learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/store-interaction")
def store_interaction_for_learning(
    brand_id: int,
    interaction_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Store interaction data for learning"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        # Validate required fields
        required_fields = ["user_message", "ai_prediction"]
        for field in required_fields:
            if field not in interaction_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add brand_id to interaction data
        interaction_data["brand_id"] = brand_id
        
        self_learning_service = SelfLearningService(db)
        self_learning_service.store_interaction_for_learning(brand_id, interaction_data)
        
        return {
            "success": True,
            "message": "Interaction stored for learning",
            "brand_id": brand_id
        }
        
    except Exception as e:
        logger.error(f"Error storing interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/brand/{brand_id}/cleanup")
def cleanup_old_data(
    brand_id: int,
    days: int = Query(90, description="Days of data to keep"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up old learning data"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        self_learning_service.cleanup_old_data(brand_id, days)
        
        return {
            "success": True,
            "message": f"Cleaned up data older than {days} days",
            "brand_id": brand_id
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/training-status")
def get_training_status(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training status for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        brand_memory = self_learning_service.get_brand_memory(brand_id)
        
        # Check if models exist
        has_models = bool(brand_memory.get("intent_classifier"))
        
        # Get training data count
        from app.models import AILearningData
        training_data_count = db.query(AILearningData).filter(
            AILearningData.brand_id == brand_id
        ).count()
        
        # Get recent data count
        from datetime import datetime, timedelta
        recent_data_count = db.query(AILearningData).filter(
            AILearningData.brand_id == brand_id,
            AILearningData.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "success": True,
            "brand_id": brand_id,
            "training_status": {
                "has_trained_models": has_models,
                "total_training_data": training_data_count,
                "recent_training_data": recent_data_count,
                "can_train": training_data_count >= 50,
                "model_metrics": brand_memory.get("metrics", {}),
                "last_training": brand_memory.get("last_trained")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/knowledge-similarity")
def find_similar_knowledge(
    brand_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find similar knowledge for given text"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        brand_memory = self_learning_service.get_brand_memory(brand_id)
        
        similar_knowledge = self_learning_service._find_similar_knowledge(
            brand_id, text, brand_memory
        )
        
        return {
            "success": True,
            "brand_id": brand_id,
            "text": text,
            "similar_knowledge": similar_knowledge
        }
        
    except Exception as e:
        logger.error(f"Error finding similar knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/pattern-matching")
def find_matching_patterns(
    brand_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find matching conversation patterns"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        brand_memory = self_learning_service.get_brand_memory(brand_id)
        
        matching_patterns = self_learning_service._find_matching_patterns(
            brand_id, text, brand_memory
        )
        
        return {
            "success": True,
            "brand_id": brand_id,
            "text": text,
            "matching_patterns": matching_patterns
        }
        
    except Exception as e:
        logger.error(f"Error finding matching patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/best-template")
def find_best_response_template(
    brand_id: int,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find best response template for given text"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        self_learning_service = SelfLearningService(db)
        brand_memory = self_learning_service.get_brand_memory(brand_id)
        
        best_template = self_learning_service._find_best_response_template(
            brand_id, text, brand_memory
        )
        
        return {
            "success": True,
            "brand_id": brand_id,
            "text": text,
            "best_template": best_template
        }
        
    except Exception as e:
        logger.error(f"Error finding best template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/global/status")
def get_global_learning_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get global learning status (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get overall statistics
        from app.models import AILearningData, Brand, ConversationPattern, BrandKnowledge
        
        total_brands = db.query(Brand).count()
        total_learning_data = db.query(AILearningData).count()
        total_patterns = db.query(ConversationPattern).count()
        total_knowledge = db.query(BrandKnowledge).count()
        
        # Get brands with trained models
        import os
        brand_models_path = "backend/brand_models"
        brands_with_models = 0
        if os.path.exists(brand_models_path):
            brands_with_models = len([d for d in os.listdir(brand_models_path) 
                                    if os.path.isdir(os.path.join(brand_models_path, d))])
        
        return {
            "success": True,
            "global_status": {
                "total_brands": total_brands,
                "brands_with_models": brands_with_models,
                "total_learning_data": total_learning_data,
                "total_patterns": total_patterns,
                "total_knowledge": total_knowledge,
                "learning_coverage": (brands_with_models / total_brands * 100) if total_brands > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting global learning status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/global/train-all")
def train_all_brands(
    force: bool = Query(False, description="Force training for all brands"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train models for all brands (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get all brands
        brands = db.query(Brand).all()
        
        if background_tasks:
            # Run training in background for all brands
            self_learning_service = SelfLearningService(db)
            for brand in brands:
                background_tasks.add_task(
                    self_learning_service.train_brand_specific_models,
                    brand.id,
                    force
                )
            
            return {
                "success": True,
                "message": f"Training started for {len(brands)} brands in background",
                "brands_count": len(brands)
            }
        else:
            # Run training synchronously
            results = []
            self_learning_service = SelfLearningService(db)
            
            for brand in brands:
                try:
                    result = self_learning_service.train_brand_specific_models(brand.id, force)
                    results.append({
                        "brand_id": brand.id,
                        "brand_name": brand.name,
                        "status": result["status"],
                        "message": result["message"]
                    })
                except Exception as e:
                    results.append({
                        "brand_id": brand.id,
                        "brand_name": brand.name,
                        "status": "error",
                        "message": str(e)
                    })
            
            return {
                "success": True,
                "message": f"Training completed for {len(brands)} brands",
                "results": results
            }
        
    except Exception as e:
        logger.error(f"Error training all brands: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 