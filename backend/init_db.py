import logging
from app.database import SessionLocal
from app import crud, schemas
from app.models import RoleEnum

# --- Add these lines to create tables before any CRUD ---
from app.models import Base
from app.database import engine
Base.metadata.create_all(bind=engine)
# -------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    db = SessionLocal()

    # Check if an admin user already exists
    admin_user = crud.get_user_by_email(db, email="admin@complainthub.com")
    if not admin_user:
        logger.info("Creating initial admin user...")
        user_in = schemas.UserCreate(
            email="admin@complainthub.com",
            password="a_very_secure_password",
            full_name="Platform Admin",
            role=RoleEnum.admin
        )
        crud.create_user(db=db, user=user_in)
        logger.info("Admin user created successfully.")
    else:
        logger.info("Admin user already exists. Skipping creation.")

    # Check if a default brand already exists
    default_brand = crud.get_brand_by_name(db, name="Default Brand Inc.")
    if not default_brand:
        logger.info("Creating initial brand...")
        brand_in = schemas.BrandCreate(
            name="Default Brand Inc.",
            support_email="support@defaultbrand.com"
        )
        crud.create_brand(db, brand=brand_in)
        logger.info("Default brand created successfully.")
    else:
        logger.info("Default brand already exists. Skipping creation.")


if __name__ == "__main__":
    logger.info("Creating initial data...")
    init_db()
    logger.info("Initial data created.")