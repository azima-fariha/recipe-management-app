from models import User
from sqlalchemy.orm import Session
from schemas import UserUpdateDto

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).get(user_id)

def create_user(db:Session, user_data: User) -> User:
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

def update_user(db: Session, user: User, user_data: UserUpdateDto) -> User:
    if user:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    return None