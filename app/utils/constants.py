from enum import Enum

class Platform(str, Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

class RegistrationState(str, Enum):
    INITIAL = "initial"
    ASKING_NAME = "asking_name"
    ASKING_EMAIL = "asking_email"
    ASKING_PHONE = "asking_phone"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"

FAQ = {
    "Что такое ESG?": """
ESG (Environmental, Social, Governance) - это подход к оценке деятельности компаний, учитывающий экологические, социальные и управленческие факторы.
    """,
    "Когда и где пройдет форум?": """
Форум пройдет 17 июня 2025 года в Москве, в Точке кипения – Коммуна (2-й Донской проезд, д. 9, стр. 3).
    """,
    "Как зарегистрироваться?": """
Для регистрации просто следуйте инструкциям бота. Вам нужно будет указать ФИО, email и номер телефона.
    """,
    "Сколько стоит участие?": """
Участие в форуме бесплатное, но требуется предварительная регистрация.
    """,
    "Как связаться с организаторами?": """
Вы можете связаться с организаторами через:
- Telegram: @LEXARKHOVA
- Email: info@esgtech.pro
- Телефон: +7 999 822-12-77
    """
}

SUPPORT_KEYWORDS = [
    "оператор",
    "человек",
    "поддержка",
    "помощь",
    "вопрос",
    "проблема",
    "связаться",
    "консультация"
] 