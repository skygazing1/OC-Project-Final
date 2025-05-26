from app.core.database import get_db
from app.services.notification import NotificationService

def main():
    db = next(get_db())
    notification_service = NotificationService(db)
    notification_service.send_bulk_reminders()

if __name__ == "__main__":
    main() 