from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)  # 'telegram' or 'whatsapp'
    platform_user_id = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_registered = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    feedback_submitted = Column(Boolean, default=False)
    receive_reminders = Column(Boolean, default=False)
    reminder_sent_week = Column(Boolean, default=False)
    reminder_sent_3days = Column(Boolean, default=False)
    reminder_sent_1day = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.full_name} ({self.platform})>" 