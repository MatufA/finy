from dataclasses import dataclass
import os


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
