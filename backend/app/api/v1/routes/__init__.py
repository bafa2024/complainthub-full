from .crm import router as crm_router
from .security import router as security_router
from app.api.v1.endpoints.self_learning import router as self_learning_router
from app.api.v1.endpoints.conversation import router as conversation_router
from .tickets import router as tickets_router
from .tickets_extended import router as tickets_extended_router
from .seo import router as seo_router
from .auth import router as auth_router
from .webhook import router as webhook_router
from .analytics import router as analytics_router
from .users import router as users_router
from .admin import router as admin_router

# Import the new brand management router
from app.api.v1.endpoints.brand_management import router as brand_management_router

api_router.include_router(crm_router, prefix="/crm", tags=["crm"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
api_router.include_router(self_learning_router, prefix="/self-learning", tags=["self-learning"])
api_router.include_router(conversation_router, prefix="/conversation", tags=["conversation"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(tickets_extended_router, prefix="/tickets_extended", tags=["tickets_extended"])
api_router.include_router(seo_router, prefix="/seo", tags=["seo"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(brand_management_router, prefix="/brand-management", tags=["Brand Management"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
