from enum import Enum

class Platform(str, Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

# class RegistrationState(str, Enum): # Удаляем
#     INITIAL = "initial"
#     ASKING_NAME = "asking_name"
#     ASKING_EMAIL = "asking_email"
#     ASKING_PHONE = "asking_phone"
#     CONFIRMATION = "confirmation"
#     COMPLETED = "completed"

# FAQ = { # Удаляем
#     ...
# }

# SUPPORT_KEYWORDS = [ # Удаляем
#     ...
# ] 