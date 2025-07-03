from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == "aj_brand@gmail.com").first()
if user:
    user.brand_id = 22  # Assign to 'aj brand'
    db.commit()
    print("User assigned to brand!")
else:
    print("User not found.")
db.close() 