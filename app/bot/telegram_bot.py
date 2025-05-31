import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from app.core.config import settings
from app.core.database import get_db, init_db
from app.services.registration import RegistrationService
from app.utils.constants import Platform

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Определим данные для кнопок и соответствующие тексты ответов
# Можно перенести в settings или constants, но для примера оставим здесь
BUTTONS = {
    "info": "Информация о форуме",
    "faq": "Часто задаваемые вопросы",
    "contact": "Связь и помощь",
    "register_site": "Как зарегистрироваться на сайте",
    "reminders_on": "Получать напоминания", # Кнопка для включения напоминаний
    "reminders_off": "Отключить напоминания", # Кнопка для отключения напоминаний
}

# Тексты ответов (можно также вынести)
RESPONSES = {
    "info": settings.Messages.EVENT_INFO.format(
        date=settings.EVENT_DATE,
        location=settings.EVENT_LOCATION,
        link=settings.EVENT_LINK
    ),
    "faq": """
Часто задаваемые вопросы:

• Что такое ESG?
ESG (Environmental, Social, Governance) - это подход к оценке деятельности компаний, учитывающий экологические, социальные и управленческие факторы.

• Когда и где пройдет форум?
Форум пройдет {} в {}.

• Как зарегистрироваться на сайте?
Инструкция по регистрации: [ссылка на инструкцию/сайт]

• Сколько стоит участие?
Участие в форуме бесплатное, но требуется предварительная регистрация на сайте.

• Как связаться с организаторами?
Вы можете связаться с организаторами через:
Telegram: {}
Email: {}
Телефон: {}
""".format(
        settings.EVENT_DATE,
        settings.EVENT_LOCATION,
        settings.ADMIN_TELEGRAM,
        settings.ADMIN_EMAIL,
        settings.ADMIN_PHONE
    ),
    "contact": settings.Messages.SUPPORT_MESSAGE.format(
        telegram=settings.ADMIN_TELEGRAM,
        email=settings.ADMIN_EMAIL,
        phone=settings.ADMIN_PHONE
    ),
    "register_site": """
Для регистрации на форум, пожалуйста, перейдите на сайт:
{}

Следуйте инструкциям на сайте для завершения регистрации.
""".format(settings.EVENT_LINK),
    "reminders_on_success": "Вы подписались на напоминания о форуме. Я пришлю уведомления за неделю, 3 дня и за день до начала.",
    "reminders_off_success": "Вы отписались от напоминаний о форуме.",
    "welcome": """
Добро пожаловать в бот ESG TECH Forum!

Форум состоится {} в {}.

Я здесь, чтобы предоставить вам информацию о форуме и помочь с регистрацией на нашем сайте.

Выберите один из пунктов меню ниже или воспользуйтесь командами /info, /faq, /contact.
""".format(settings.EVENT_DATE, settings.EVENT_LOCATION)
}


async def send_main_menu(update: Update, user, message_text: str) -> None:
    """Отправляет сообщение с главным меню."""
    keyboard = [
        [InlineKeyboardButton(BUTTONS["info"], callback_data="info")],
        [InlineKeyboardButton(BUTTONS["faq"], callback_data="faq")],
        [InlineKeyboardButton(BUTTONS["contact"], callback_data="contact")],
        [InlineKeyboardButton(BUTTONS["register_site"], callback_data="register_site")],
    ]

    # Добавляем кнопку управления напоминаниями в зависимости от статуса пользователя
    if user and user.receive_reminders:
        keyboard.append([InlineKeyboardButton(BUTTONS["reminders_off"], callback_data="reminders_off")])
    else:
        keyboard.append([InlineKeyboardButton(BUTTONS["reminders_on"], callback_data="reminders_on")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверяем, есть ли у update.message метод reply_text (для команды /start)
    if hasattr(update, 'message') and update.message:
         await update.message.reply_text(message_text, reply_markup=reply_markup)
    # Если нет (для callbackQuery), используем edit_message_text
    elif hasattr(update, 'callback_query') and update.callback_query:
         await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command. Greets user and shows main menu."""
    db = next(get_db())
    registration_service = RegistrationService(db)

    # Get or create user in DB
    user = registration_service.create_user(Platform.TELEGRAM, str(update.effective_user.id))

    # Передаем объект пользователя в send_main_menu
    await send_main_menu(update, user, RESPONSES["welcome"])

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button clicks."""
    query = update.callback_query
    await query.answer() # Отвечаем на callbackQuery, чтобы кнопка не висела

    db = next(get_db())
    registration_service = RegistrationService(db)
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))

    # Получаем данные из кнопки
    button_data = query.data

    message_text_to_edit = "" # Сообщение для редактирования

    # Обрабатываем нажатия кнопок информации
    if button_data in ["info", "faq", "contact", "register_site"]:
        message_text_to_edit = RESPONSES.get(button_data, "Неизвестная информация.")

    # Обрабатываем нажатия кнопок управления напоминаниями
    elif button_data == "reminders_on":
        if user:
            user.receive_reminders = True
            db.commit()
            message_text_to_edit = RESPONSES["reminders_on_success"]
    elif button_data == "reminders_off":
        if user:
            user.receive_reminders = False
            db.commit()
            message_text_to_edit = RESPONSES["reminders_off_success"]
    else:
        message_text_to_edit = "Неизвестная команда."

    # Обновляем сообщение, сохраняя текущую разметку клавиатуры
    # Важно получить актуального пользователя для правильного отображения кнопки напоминаний
    updated_user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    await send_main_menu(update, updated_user, message_text_to_edit)


# Нам больше не нужны отдельные обработчики для faq и event_info, так как их обрабатывает handle_button_click.
# async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle FAQ questions."""
#     # Этот код будет заменен логикой из handle_button_click
#     pass

# async def handle_event_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle event information request."""
#      # Этот код будет заменен логикой из handle_button_click
#     pass

# Обработчик текстовых сообщений, который не является командой.
# Можно использовать для обработки кнопок ReplyKeyboard, если бы мы их использовали,
# или для обработки произвольного текста, если нужна какая-то другая логика (например, поиск по FAQ)
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    # Пока просто игнорируем текстовые сообщения, не соответствующие командам или callback'ам кнопок
    # Или можно отправить основное меню или сообщение о том, что бот работает по кнопкам.
    # await send_main_menu(update, "Пожалуйста, используйте кнопки меню:") # Опционально
    pass


# Команда для включения напоминаний (альтернатива кнопке или в дополнение к ней)
async def register_for_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = next(get_db())
    registration_service = RegistrationService(db)
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    if user:
        user.receive_reminders = True
        db.commit()
        await update.message.reply_text(RESPONSES["reminders_on_success"])
    else:
        # Если пользователя нет (что маловероятно после /start), создадим его
        registration_service.create_user(Platform.TELEGRAM, str(update.effective_user.id))
        user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
        if user:
             user.receive_reminders = True
             db.commit()
             await update.message.reply_text(RESPONSES["reminders_on_success"])


# Команда для отключения напоминаний
async def unregister_for_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = next(get_db())
    registration_service = RegistrationService(db)
    user = registration_service.get_user(Platform.TELEGRAM, str(update.effective_user.id))
    if user:
        user.receive_reminders = False
        db.commit()
        await update.message.reply_text(RESPONSES["reminders_off_success"])


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # Добавляем обработчик нажатий на инлайн-кнопки
    application.add_handler(CallbackQueryHandler(handle_button_click))

    # Добавляем обработчики команд для управления напоминаниями
    # application.add_handler(CommandHandler('reminders_on', register_for_reminders_command))
    # application.add_handler(CommandHandler('reminders_off', unregister_for_reminders_command))

    # Добавляем обработчик любых текстовых сообщений, которые не являются командами (опционально)
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))


    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 