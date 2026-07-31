from models import User
from sqlalchemy.orm import Session

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).get(user_id)

def create_user(db:Session, user_data: User) -> User:
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data