from models import User
from schemas import UserUpdateDto
from sqlalchemy.orm import Session


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).get(user_id)

def create_user(db:Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_data: UserUpdateDto) -> User:
    if user:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    return None

def delete_user(db: Session, user: User) -> None:
    if user:
        db.delete(user)
        db.commit()
