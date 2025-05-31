import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db, init_db
from app.models.user import User
from app.utils.constants import Platform
from telegram import Bot # Импортируем Bot для отправки сообщений
from twilio.rest import Client # Импортируем Client для WhatsApp

# Initialize database
init_db()

# Инициализируем бота Telegram
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

# Инициализируем клиент Twilio для WhatsApp
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

async def send_telegram_message(chat_id: str, message: str):
    """Отправляет сообщение пользователю Telegram."""
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения Telegram пользователю {chat_id}: {e}")
        return False

def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Отправляет сообщение пользователю WhatsApp через Twilio."""
    try:
        # Twilio требует номер в формате "whatsapp:+номер"
        message = twilio_client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            body=message,
            to=f"whatsapp:{to_number}"
        )
        print(f"Сообщение WhatsApp отправлено пользователю {to_number}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения WhatsApp пользователю {to_number}: {e}")
        return False

def get_users_for_reminders(db: Session) -> list[User]:
    """Получает список пользователей, подписанных на напоминания."""
    return db.query(User).filter(
        User.receive_reminders == True
    ).all()

async def send_reminders():
    """Отправляет напоминания пользователям."""
    db = next(get_db())
    users_to_notify = get_users_for_reminders(db)

    event_date_str = settings.EVENT_DATE # Дата события из настроек
    try:
        event_date = datetime.strptime(event_date_str, "%d %B %Y")
    except ValueError:
        print(f"Ошибка парсинга даты события: {event_date_str}. Проверьте формат в settings.EVENT_DATE.")
        db.close()
        return

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Расчет дат напоминаний
    date_week_before = event_date - timedelta(days=7)
    date_3days_before = event_date - timedelta(days=3)
    date_1day_before = event_date - timedelta(days=1)

    # Тексты напоминаний (можно вынести в настройки/константы)
    reminder_messages = {
        "week": f"Напоминание! До ESG TECH Forum осталась неделя! Форум состоится {event_date_str}. Подробности: {settings.EVENT_LINK}",
        "3days": f"Напоминание! До ESG TECH Forum осталось 3 дня! Форум состоится {event_date_str}. Подробности: {settings.EVENT_LINK}",
        "1day": f"Последнее напоминание! ESG TECH Forum завтра! {event_date_str} в {settings.EVENT_LOCATION}. Подробности: {settings.EVENT_LINK}"
    }

    for user in users_to_notify:
        # Напоминание за неделю
        if today == date_week_before.replace(hour=0, minute=0, second=0, microsecond=0) and not user.reminder_sent_week:
            if user.platform == Platform.TELEGRAM:
                if await send_telegram_message(user.platform_user_id, reminder_messages["week"]):
                    user.reminder_sent_week = True
                    db.commit()
                    print(f"Отправлено напоминание за неделю пользователю {user.platform_user_id} ({user.platform})")
            elif user.platform == Platform.WHATSAPP:
                if send_whatsapp_message(user.platform_user_id, reminder_messages["week"]):
                    user.reminder_sent_week = True
                    db.commit()
                    print(f"Отправлено напоминание за неделю пользователю {user.platform_user_id} ({user.platform})")

        # Напоминание за 3 дня
        if today == date_3days_before.replace(hour=0, minute=0, second=0, microsecond=0) and not user.reminder_sent_3days:
            if user.platform == Platform.TELEGRAM:
                if await send_telegram_message(user.platform_user_id, reminder_messages["3days"]):
                    user.reminder_sent_3days = True
                    db.commit()
                    print(f"Отправлено напоминание за 3 дня пользователю {user.platform_user_id} ({user.platform})")
            elif user.platform == Platform.WHATSAPP:
                if send_whatsapp_message(user.platform_user_id, reminder_messages["3days"]):
                    user.reminder_sent_3days = True
                    db.commit()
                    print(f"Отправлено напоминание за 3 дня пользователю {user.platform_user_id} ({user.platform})")

        # Напоминание за 1 день
        if today == date_1day_before.replace(hour=0, minute=0, second=0, microsecond=0) and not user.reminder_sent_1day:
            if user.platform == Platform.TELEGRAM:
                if await send_telegram_message(user.platform_user_id, reminder_messages["1day"]):
                    user.reminder_sent_1day = True
                    db.commit()
                    print(f"Отправлено напоминание за 1 день пользователю {user.platform_user_id} ({user.platform})")
            elif user.platform == Platform.WHATSAPP:
                if send_whatsapp_message(user.platform_user_id, reminder_messages["1day"]):
                    user.reminder_sent_1day = True
                    db.commit()
                    print(f"Отправлено напоминание за 1 день пользователю {user.platform_user_id} ({user.platform})")

    db.close()

if __name__ == "__main__":
    print("Запуск скрипта отправки напоминаний...")
    asyncio.run(send_reminders())
    print("Скрипт отправки напоминаний завершен.") 