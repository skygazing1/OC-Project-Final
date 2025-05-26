import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from app.core.config import settings
from app.core.database import get_db, init_db
from app.services.registration import RegistrationService
from app.services.notification import NotificationService
from app.utils.constants import Platform, RegistrationState, FAQ, SUPPORT_KEYWORDS

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for their name."""
    db = next(get_db())
    registration_service = RegistrationService(db)
    
    # Get or create user
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    if not user:
        user = registration_service.create_user(Platform.TELEGRAM, str(update.effective_user.id))
    
    # Send welcome message
    await update.message.reply_text(
        settings.Messages.WELCOME.format(
            date=settings.EVENT_DATE,
            location=settings.EVENT_LOCATION
        ) + "\n\nВаши данные будут храниться только для регистрации на форум. Подробнее: info@esgtech.pro"
    )
    
    return RegistrationState.ASKING_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's name input."""
    db = next(get_db())
    registration_service = RegistrationService(db)
    
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    is_valid, error = registration_service.update_user_name(user, update.message.text)
    
    if not is_valid:
        await update.message.reply_text(error)
        return RegistrationState.ASKING_NAME
    
    await update.message.reply_text("Спасибо! Теперь, пожалуйста, введите ваш email:")
    return RegistrationState.ASKING_EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's email input."""
    db = next(get_db())
    registration_service = RegistrationService(db)
    
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    is_valid, error = registration_service.update_user_email(user, update.message.text)
    
    if not is_valid:
        await update.message.reply_text(error)
        return RegistrationState.ASKING_EMAIL
    
    await update.message.reply_text("Отлично! Теперь, пожалуйста, введите ваш номер телефона:")
    return RegistrationState.ASKING_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's phone input."""
    db = next(get_db())
    registration_service = RegistrationService(db)
    
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    is_valid, error = registration_service.update_user_phone(user, update.message.text)
    
    if not is_valid:
        await update.message.reply_text(error)
        return RegistrationState.ASKING_PHONE
    
    # Show confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Пожалуйста, проверьте ваши данные:\n\n"
        f"👤 ФИО: {user.full_name}\n"
        f"📧 Email: {user.email}\n"
        f"📱 Телефон: {user.phone}\n\n"
        f"Всё верно?",
        reply_markup=reply_markup
    )
    
    return RegistrationState.CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle registration confirmation."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Регистрация отменена. Начните заново с помощью команды /start")
        return ConversationHandler.END
    
    db = next(get_db())
    registration_service = RegistrationService(db)
    notification_service = NotificationService(db)
    
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    registration_service.complete_registration(user)
    
    # Send confirmation
    await notification_service.send_registration_confirmation(user)
    
    await query.edit_message_text(
        "✅ Регистрация успешно завершена!\n\n"
        f"Мы отправили подтверждение на ваш email: {user.email}\n\n"
        "До встречи на форуме!"
    )
    
    return ConversationHandler.END

async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle FAQ questions."""
    text = update.message.text.lower()
    
    # Check if it's a support request
    if any(keyword in text for keyword in SUPPORT_KEYWORDS):
        await update.message.reply_text(
            settings.Messages.SUPPORT_MESSAGE.format(
                telegram=settings.ADMIN_TELEGRAM,
                email=settings.ADMIN_EMAIL,
                phone=settings.ADMIN_PHONE
            )
        )
        return
    
    # Check FAQ
    for question, answer in FAQ.items():
        if question.lower() in text:
            await update.message.reply_text(answer)
            return
    
    # If no FAQ match, show all available questions
    faq_text = "Вы можете задать вопрос по следующим темам:\n\n"
    for question in FAQ.keys():
        faq_text += f"• {question}\n"
    
    await update.message.reply_text(faq_text)

async def handle_event_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle event information request."""
    await update.message.reply_text(
        settings.Messages.EVENT_INFO.format(
            date=settings.EVENT_DATE,
            location=settings.EVENT_LOCATION,
            link=settings.EVENT_LINK
        )
    )

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = next(get_db())
    registration_service = RegistrationService(db)
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    if not user or not user.is_registered:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start.")
        return
    if not context.args:
        await update.message.reply_text("Пожалуйста, отправьте отзыв в формате: /feedback ваш_отзыв")
        return
    feedback_text = ' '.join(context.args)
    registration_service.save_feedback(user, feedback_text)
    await update.message.reply_text("Спасибо за ваш отзыв!")

async def delete_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = next(get_db())
    registration_service = RegistrationService(db)
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    if not user:
        await update.message.reply_text("Вы не зарегистрированы.")
        return
    registration_service.delete_user(user)
    await update.message.reply_text("Ваши данные удалены из системы. Спасибо!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Доступные команды:\n"
        "/start — начать регистрацию\n"
        "/info — информация о форуме\n"
        "/feedback ваш_отзыв — оставить отзыв о форуме\n"
        "/delete_me — удалить свои данные из системы\n"
        "/help — список всех команд\n"
        "\nТакже вы можете задавать вопросы о форуме или написать 'оператор', чтобы связаться с поддержкой."
    )
    await update.message.reply_text(help_text)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RegistrationState.ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            RegistrationState.ASKING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            RegistrationState.ASKING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            RegistrationState.CONFIRMATION: [CallbackQueryHandler(handle_confirmation)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('info', handle_event_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq))
    application.add_handler(CommandHandler('feedback', feedback))
    application.add_handler(CommandHandler('delete_me', delete_me))
    application.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 