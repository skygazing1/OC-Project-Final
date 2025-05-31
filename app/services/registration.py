from sqlalchemy.orm import Session
from app.models.user import User
# from app.utils.validators import validate_name, validate_email, validate_phone # Удаляем валидаторы
from app.utils.constants import Platform
# from typing import Tuple, Optional # Удаляем Optional, так как get_user может остаться
from typing import Optional

class RegistrationService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, platform: Platform, platform_user_id: str) -> User:
        """Create a new user in the database if not exists."""
        user = self.get_user(platform, platform_user_id)
        if user is None:
            user = User(
                platform=platform,
                platform_user_id=platform_user_id,
                full_name="", # Оставляем пустые, так как регистрация через бота убрана
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

    # Удаляем все методы, связанные с обновлением данных регистрации, завершением регистрации, удалением и обратной связью.
    # def update_user_name(...): ...
    # def update_user_email(...): ...
    # def update_user_phone(...): ...
    # def complete_registration(...): ...
    # def is_registration_complete(...): ...
    # def delete_user(...): ...
    # def save_feedback(...): ... 