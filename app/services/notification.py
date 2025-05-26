from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.constants import Platform
from app.core.config import settings
import aiohttp
import json
import asyncio
import smtplib
from email.mime.text import MIMEText

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    async def send_telegram_message(self, chat_id: str, message: str) -> bool:
        """Send message via Telegram Bot API."""
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    return response.status == 200
            except Exception:
                return False

    async def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send message via Twilio WhatsApp API."""
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        data = {
            "From": f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            "To": f"whatsapp:{to_number}",
            "Body": message
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, auth=aiohttp.BasicAuth(*auth), data=data) as response:
                    return response.status == 201
            except Exception:
                return False

    def send_email(self, to_email, subject, body):
        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT
        user = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        from_email = settings.EMAIL_FROM or user

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())

    async def send_registration_confirmation(self, user: User) -> bool:
        """Send registration confirmation to user."""
        message = f"""
✅ Регистрация успешно завершена!

Спасибо за регистрацию на ESG TECH Forum!

Ваши данные:
👤 ФИО: {user.full_name}
📧 Email: {user.email}
📱 Телефон: {user.phone}

Дата мероприятия: {settings.EVENT_DATE}
Место: {settings.EVENT_LOCATION}

До встречи на форуме!
        """
        
        # Отправка email
        try:
            self.send_email(
                user.email,
                "ESG TECH Forum — подтверждение регистрации",
                message
            )
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
        
        if user.platform == Platform.TELEGRAM:
            return await self.send_telegram_message(user.platform_user_id, message)
        else:
            return await self.send_whatsapp_message(user.phone, message)

    async def send_event_reminder(self, user: User) -> bool:
        """Send event reminder to user."""
        message = f"""
🔔 Напоминание о мероприятии!

До ESG TECH Forum осталось 3 дня!

📅 Дата: {settings.EVENT_DATE}
📍 Место: {settings.EVENT_LOCATION}

Не забудьте посетить мероприятие!

Подробности: {settings.EVENT_WEBSITE}
        """
        
        if user.platform == Platform.TELEGRAM:
            return await self.send_telegram_message(user.platform_user_id, message)
        else:
            return await self.send_whatsapp_message(user.phone, message)

    def get_users_for_reminder(self) -> list[User]:
        """Get users who need to receive reminder."""
        event_date = datetime.strptime(settings.EVENT_DATE, "%d %B %Y")
        reminder_date = event_date - timedelta(days=3)
        
        return self.db.query(User).filter(
            User.is_registered == True,
            User.reminder_sent == False,
            User.registration_date <= reminder_date
        ).all()

    def mark_reminder_sent(self, user: User) -> None:
        """Mark reminder as sent for user."""
        user.reminder_sent = True
        self.db.commit()

    def send_bulk_reminders(self):
        users = self.db.query(User).filter(User.is_registered == True, User.reminder_sent == False).all()
        loop = asyncio.get_event_loop()
        for user in users:
            loop.run_until_complete(self.send_event_reminder(user))
            self.mark_reminder_sent(user)
        print(f"Sent reminders to {len(users)} users.") 