from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.validators import validate_name, validate_email, validate_phone
from app.utils.constants import Platform
from typing import Tuple, Optional

class RegistrationService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, platform: Platform, platform_user_id: str) -> User:
        """Create a new user in the database."""
        user = User(
            platform=platform,
            platform_user_id=platform_user_id,
            full_name="",
            email="",
            phone=""
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, platform: Platform, platform_user_id: str) -> Optional[User]:
        """Get user by platform and platform user ID."""
        return self.db.query(User).filter(
            User.platform == platform,
            User.platform_user_id == platform_user_id
        ).first()

    def update_user_name(self, user: User, name: str) -> Tuple[bool, str]:
        """Update user's name with validation."""
        is_valid, error = validate_name(name)
        if not is_valid:
            return False, error
        
        user.full_name = name
        self.db.commit()
        return True, ""

    def update_user_email(self, user: User, email: str) -> Tuple[bool, str]:
        """Update user's email with validation."""
        is_valid, error = validate_email(email)
        if not is_valid:
            return False, error
        
        user.email = email
        self.db.commit()
        return True, ""

    def update_user_phone(self, user: User, phone: str) -> Tuple[bool, str]:
        """Update user's phone with validation."""
        is_valid, error = validate_phone(phone)
        if not is_valid:
            return False, error
        
        user.phone = phone
        self.db.commit()
        return True, ""

    def complete_registration(self, user: User) -> None:
        """Mark user registration as completed."""
        user.is_registered = True
        self.db.commit()

    def is_registration_complete(self, user: User) -> bool:
        """Check if user has completed registration."""
        return all([
            user.full_name,
            user.email,
            user.phone,
            user.is_registered
        ])

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def save_feedback(self, user: User, feedback: str) -> None:
        user.feedback_submitted = True
        # Можно добавить отдельную таблицу для отзывов, но для простоты сохраним в лог
        print(f"Feedback from {user.platform} {user.platform_user_id}: {feedback}")
        self.db.commit() 