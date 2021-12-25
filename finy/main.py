from time import sleep

import logging
from logging.config import dictConfig
import telegram
from telegram.error import TelegramError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .Config import Config, log_config

app = FastAPI(debug=True)
dictConfig(log_config)
config = Config
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
assert config.telegram_config.bot_token is not None, 'TOKEN is none'
bot = telegram.Bot(token=config.telegram_config.bot_token)
authUsers = None
if Config.authorized_users.users:
    authUsers = [user for user in Config.authorized_users.users.split(';')]
    logger.info(f'authorized users: {authUsers}')
else:
    logger.error("no user configured")


@app.get("/hello/{name}")
async def helloname(name: str):
    """
    Returns a Hello to the User with a wave emoji
    """
    return f"Hello {name} 👋"


@app.get("/index.html ")
async def health():
    """
    Returns a Hello to the User with a wave emoji
    """
    return f"alive"


@app.post(f"/{config.telegram_config.bot_token}")
async def respond(req: Request):
    # retrieve the message in JSON and then transform it to Telegram object
    body = await req.json()
    update = telegram.Update.de_json(body, bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    logger.info(f'chat id: {chat_id}, user name: {update.message.chat.full_name}')

    if str(chat_id) not in authUsers:
        return 'false'

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    logger.info("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Hi I'm Finy and I'll be you financial assistance. Please fill free to let me know about 
       all your expenses and I'll track it. In the future I'll be generate a reports for you. 
       """
        # send the welcoming message
        bot.sendChatAction(chat_id=chat_id, action="typing")
        sleep(1.5)
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    else:
        try:
            bot.sendChatAction(chat_id=chat_id, action="typing")
            cost, category = text.split(' ')
            sleep(1.5)
            ans = f"""
                    did you spent {cost} for {category}?
                    """
            bot.sendMessage(chat_id=chat_id, text=ans, reply_to_message_id=msg_id)
        except (TelegramError, ValueError) as e:
            logger.error(e)
            # if things went wrong
            bot.sendMessage(chat_id=chat_id,
                            text="I'm not understand please try again",
                            reply_to_message_id=msg_id)

    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
async def set_webhook(req: Request):
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    webhook = f'{config.heroku_config.url}/{config.telegram_config.bot_token}'
    logger.info(f'set webhook {webhook}')
    s = bot.setWebhook(webhook)
    # something to let us know things work
    if s:
        logger.info("webhook setup")
        return JSONResponse(
            status_code=200,
            content={"message": "webhook setup ok"},
        )
    else:
        logger.info("webhook setup failed")
        return JSONResponse(
            status_code=500,
            content={"message": "webhook setup failed"},
        )
