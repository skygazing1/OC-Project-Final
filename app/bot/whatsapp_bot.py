from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.core.config import settings
from app.core.database import get_db, init_db
from app.services.registration import RegistrationService
from app.services.notification import NotificationService
from app.utils.constants import Platform, RegistrationState, FAQ, SUPPORT_KEYWORDS
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

app = FastAPI()

# Store user states in memory (in production, use Redis or similar)
user_states = {}

def get_user_state(phone: str) -> str:
    """Get user's current state."""
    return user_states.get(phone, RegistrationState.INITIAL)

def set_user_state(phone: str, state: str) -> None:
    """Set user's current state."""
    user_states[phone] = state

@app.post("/webhook")
async def webhook(request: Request) -> Response:
    """Handle incoming WhatsApp messages."""
    # Parse incoming message
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender = form_data.get('From', '').replace('whatsapp:', '')
    
    # Create response
    resp = MessagingResponse()
    msg = resp.message()
    
    # Get user state
    current_state = get_user_state(sender)
    
    # Initialize services
    db = next(get_db())
    registration_service = RegistrationService(db)
    notification_service = NotificationService(db)
    
    # Get or create user
    user = registration_service.get_user(Platform.WHATSAPP, sender)
    if not user:
        user = registration_service.create_user(Platform.WHATSAPP, sender)
    
    # Handle message based on state
    if current_state == RegistrationState.INITIAL:
        # Send welcome message
        msg.body(settings.Messages.WELCOME.format(
            date=settings.EVENT_DATE,
            location=settings.EVENT_LOCATION
        ) + "\n\nВаши данные будут храниться только для регистрации на форум. Подробнее: info@esgtech.pro")
        set_user_state(sender, RegistrationState.ASKING_NAME)
    
    elif current_state == RegistrationState.ASKING_NAME:
        is_valid, error = registration_service.update_user_name(user, incoming_msg)
        if not is_valid:
            msg.body(error)
        else:
            msg.body("Спасибо! Теперь, пожалуйста, введите ваш email:")
            set_user_state(sender, RegistrationState.ASKING_EMAIL)
    
    elif current_state == RegistrationState.ASKING_EMAIL:
        is_valid, error = registration_service.update_user_email(user, incoming_msg)
        if not is_valid:
            msg.body(error)
        else:
            msg.body("Отлично! Теперь, пожалуйста, введите ваш номер телефона:")
            set_user_state(sender, RegistrationState.ASKING_PHONE)
    
    elif current_state == RegistrationState.ASKING_PHONE:
        is_valid, error = registration_service.update_user_phone(user, incoming_msg)
        if not is_valid:
            msg.body(error)
        else:
            # Show confirmation
            msg.body(
                f"Пожалуйста, проверьте ваши данные:\n\n"
                f"👤 ФИО: {user.full_name}\n"
                f"📧 Email: {user.email}\n"
                f"📱 Телефон: {user.phone}\n\n"
                f"Всё верно? Отправьте 'да' для подтверждения или 'нет' для отмены."
            )
            set_user_state(sender, RegistrationState.CONFIRMATION)
    
    elif current_state == RegistrationState.CONFIRMATION:
        if incoming_msg.lower() in ['да', 'yes', 'y']:
            registration_service.complete_registration(user)
            await notification_service.send_registration_confirmation(user)
            msg.body(
                "✅ Регистрация успешно завершена!\n\n"
                f"Мы отправили подтверждение на ваш email: {user.email}\n\n"
                "До встречи на форуме!"
            )
            set_user_state(sender, RegistrationState.COMPLETED)
        elif incoming_msg.lower() in ['нет', 'no', 'n']:
            msg.body("Регистрация отменена. Начните заново, отправив любое сообщение.")
            set_user_state(sender, RegistrationState.INITIAL)
        else:
            msg.body("Пожалуйста, ответьте 'да' или 'нет'.")
    
    elif incoming_msg.lower().startswith('отзыв') or incoming_msg.lower().startswith('feedback'):
        if not user.is_registered:
            msg.body("Сначала завершите регистрацию.")
        else:
            feedback_text = incoming_msg.partition(' ')[2]
            registration_service.save_feedback(user, feedback_text)
            msg.body("Спасибо за ваш отзыв!")
        return Response(content=str(resp), media_type="application/xml")
    elif incoming_msg.lower() in ['удалить меня', 'delete me']:
        registration_service.delete_user(user)
        msg.body("Ваши данные удалены из системы. Спасибо!")
        return Response(content=str(resp), media_type="application/xml")
    
    else:
        # Handle FAQ and general messages
        text = incoming_msg.lower()
        
        # Check if it's a support request
        if any(keyword in text for keyword in SUPPORT_KEYWORDS):
            msg.body(settings.Messages.SUPPORT_MESSAGE.format(
                telegram=settings.ADMIN_TELEGRAM,
                email=settings.ADMIN_EMAIL,
                phone=settings.ADMIN_PHONE
            ))
            return Response(content=str(resp), media_type="application/xml")
        
        # Check FAQ
        for question, answer in FAQ.items():
            if question.lower() in text:
                msg.body(answer)
                return Response(content=str(resp), media_type="application/xml")
        
        # If no FAQ match, show all available questions
        faq_text = "Вы можете задать вопрос по следующим темам:\n\n"
        for question in FAQ.keys():
            faq_text += f"• {question}\n"
        
        msg.body(faq_text)
    
    return Response(content=str(resp), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 