# ESG TECH Forum Registration Bot

A multi-platform chat bot for registering users to the ESG TECH Forum event, supporting both Telegram and WhatsApp platforms.

## Features

- Multi-platform support (Telegram & WhatsApp)
- User registration with data validation
- Event information and FAQ
- Support system with operator handoff
- Event reminders
- Post-event feedback collection
- Multi-language support (RU/EN)

## Project Structure

```
OC-project/
├── app/
│   ├── bot/
│   │   ├── telegram_bot.py
│   │   └── whatsapp_bot.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   └── user.py
│   ├── services/
│   │   ├── registration.py
│   │   └── notification.py
│   └── utils/
│       ├── validators.py
│       └── constants.py
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   - Telegram Bot Token
   - Twilio Account SID and Auth Token
   - Database URL

## Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone

# Database
DATABASE_URL=sqlite:///./esg_bot.db

# Admin
ADMIN_TELEGRAM=@LEXARKHOVA
ADMIN_EMAIL=info@esgtech.pro
ADMIN_PHONE=+79998221277
```

## Running the Bot

1. Start the Telegram bot:
   ```bash
   python -m app.bot.telegram_bot
   ```

2. Start the WhatsApp bot:
   ```bash
   python -m app.bot.whatsapp_bot
   ```

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed

## License

MIT License

## Contact

For support or questions, contact:
- Telegram: @LEXARKHOVA
- Email: info@esgtech.pro
- Phone: +7 999 822-12-77