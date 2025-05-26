from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Bot Settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./esg_bot.db")
    
    # Admin Contact
    ADMIN_TELEGRAM: str = os.getenv("ADMIN_TELEGRAM", "@LEXARKHOVA")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "info@esgtech.pro")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "+79998221277")
    
    # Event Information
    EVENT_DATE: str = "17 июня 2025"
    EVENT_LOCATION: str = "Москва, Точка кипения – Коммуна, 2-й Донской проезд, д. 9, стр. 3"
    EVENT_LINK: str = "https://leader-id.ru/events/553947"
    EVENT_WEBSITE: str = "https://esgtechforum.ru/"
    
    # Registration States
    class RegistrationState:
        INITIAL = "initial"
        ASKING_NAME = "asking_name"
        ASKING_EMAIL = "asking_email"
        ASKING_PHONE = "asking_phone"
        CONFIRMATION = "confirmation"
        COMPLETED = "completed"
    
    # Messages
    class Messages:
        WELCOME = """
Добро пожаловать в бот регистрации на ESG TECH Forum!

Я помогу вам зарегистрироваться на форум, который состоится {date} в {location}.

Давайте начнем регистрацию. Пожалуйста, введите ваше полное имя (ФИО).
        """
        
        EVENT_INFO = """
📅 Дата: {date}
📍 Место: {location}

Основные темы форума:
• ESG и устойчивое развитие
• Биотехнологии
• Климатические технологии
• Циркулярная экономика
• Инновации в ESG

Для регистрации перейдите по ссылке: {link}
        """
        
        REGISTRATION_SUCCESS = """
✅ Регистрация успешно завершена!

Мы отправили подтверждение на ваш email: {email}

До встречи на форуме!
        """
        
        SUPPORT_MESSAGE = """
Для связи с организатором:
Telegram: {telegram}
Email: {email}
Телефон: {phone}
        """

    # Email settings
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 465))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")

settings = Settings() 