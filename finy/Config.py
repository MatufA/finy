from dataclasses import dataclass
from dotenv import load_dotenv
import os

if os.getenv('ENV', '').lower() == 'local':
    load_dotenv()


@dataclass
class TelegramAuthorizedUsers:
    users = os.getenv("AUTH_USERS")


@dataclass
class TelegramBotConfig:
    bot_token = os.getenv("TOKEN")  # Telegram Bot API Key
    # chat_id = os.getenv("CHAT_ID")  # Telegram Chat ID
    bot_user_name = os.getenv("USERNAME")
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"


@dataclass
class HerokuConfig:
    url = os.getenv("URL")


@dataclass
class Config:
    telegram_config = TelegramBotConfig
    heroku_config = HerokuConfig
    authorized_users = TelegramAuthorizedUsers


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "foo-logger": {"handlers": ["default"], "level": "DEBUG"},
    },
}
