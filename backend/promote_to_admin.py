from app.database import SessionLocal
from app.models import User, RoleEnum

db = SessionLocal()
user = db.query(User).filter(User.email == "testbrand@example.com").first()
if user:
    user.role = RoleEnum.admin
    db.commit()
    print("User promoted to admin!")
else:
    print("User not found.")
db.close() 