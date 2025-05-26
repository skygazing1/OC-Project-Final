import re
from typing import Tuple

def validate_name(name: str) -> Tuple[bool, str]:
    """Validate full name format."""
    if not name or len(name.strip()) < 3:
        return False, "Имя должно содержать минимум 3 символа"
    
    # Check if name contains only letters, spaces and hyphens
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', name):
        return False, "Имя должно содержать только буквы, пробелы и дефисы"
    
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    if not email:
        return False, "Email не может быть пустым"
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Неверный формат email"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format."""
    if not phone:
        return False, "Номер телефона не может быть пустым"
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Russian phone number
    if len(digits_only) != 11 or not digits_only.startswith(('7', '8')):
        return False, "Неверный формат номера телефона. Используйте формат: +7XXXXXXXXXX"
    
    return True, "" 