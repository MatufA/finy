from time import sleep

import logging
import telegram
from fastapi import FastAPI, Request

import re
from .Config import Config

app = FastAPI()
logging.basicConfig()
config = Config
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telegram.Bot(token=config.telegram_config.bot_token)


@app.get("/hello/{name}")
async def helloname(name: str):
    """
    Returns a Hello to the User with a wave emoji
    """
    return f"Hello {name} 👋"


@app.post(f"/{config.telegram_config.bot_token}")
async def respond(req: Request):
    # retrieve the message in JSON and then transform it to Telegram object
    body = await req.json()
    update = telegram.Update.de_json(body, bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    logger.info("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Welcome to Finy bot, the bot is using the service from http://avatars.adorable.io/ to generate cool
       looking avatars based on the name you enter so please enter a name and the bot will
       reply with an avatar for your name.
       """
        # send the welcoming message
        bot.sendChatAction(chat_id=chat_id, action="typing")
        sleep(1.5)
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)
            # create the api link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # reply with a photo to the name the user sent,
            # note that you can send photos by url and telegram will fetch it for you
            bot.sendChatAction(chat_id=chat_id, action="upload_photo")
            sleep(2)
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        except Exception:
            # if things went wrong
            bot.sendMessage(chat_id=chat_id,
                            text="There was a problem in the name you used, please enter different name",
                            reply_to_message_id=msg_id)

    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=config.heroku_config.url, HOOK=config.heroku_config.url))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
