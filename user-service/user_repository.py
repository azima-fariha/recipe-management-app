from models import User
from schemas import UserUpdateDto
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class DuplicateEmailError(Exception):
    """Raised when creating a user whose email is already registered."""


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).get(user_id)

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db:Session, user: User) -> User:
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEmailError(f"Email {user.email} is already registered") from exc
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
