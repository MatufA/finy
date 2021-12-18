from time import sleep

from fastapi import FastAPI, Request
import logging

from fastapi import FastAPI, Request
import asyncio
import uvicorn

from httpx import AsyncClient
from pyngrok import ngrok

from validations import MessageBodyModel, ResponseToMessage
import re

from .Config import Config

app = FastAPI()
logging.basicConfig()
config = Config
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/webhook/{TOKEN}")
async def post_process_telegram_update(message: MessageBodyModel, request: Request):
    # print(await request.json())
    # print(message)
    return ResponseToMessage(
        **{
            "text": "Copy paste:\n\n" + message.message.text,
            "chat_id": message.message.chat.id,
        }
    )


async def request(url: str, payload: dict, debug: bool = False):
    async with AsyncClient() as client:
        req = await client.post(url, json=payload)
        if debug:
            print(req.json())
        return req


async def send_a_message_to_user(telegram_id: int, message: str) -> bool:
    message = ResponseToMessage(
        **{
            "text": message,
            "chat_id": telegram_id,
        }
    )
    req = await request(config.telegram_config.send_message_url, message.dict())
    return req.status_code == 200


async def set_telegram_webhook_url() -> bool:
    payload = {"url": f"{config.heroku_config.url}/webhook/{config.telegram_config.bot_token}"}
    req = await request(config.telegram_config.set_webhook_url, payload)
    return req.status_code == 200


@app.get("/hello/{name}")
async def helloname(name: str):
    """
    Returns a Hello to the User with a wave emoji
    """
    return f"Hello {name} 👋"


# @app.post(f"/{config.telegram_config.bot_token}")
# async def respond(req: Request):
#     # retrieve the message in JSON and then transform it to Telegram object
#     body = await req.json()
#     update = telegram.Update.de_json(body, bot)
#
#     chat_id = update.message.chat.id
#     msg_id = update.message.message_id
#
#     # Telegram understands UTF-8, so encode text for unicode compatibility
#     text = update.message.text.encode('utf-8').decode()
#     # for debugging purposes only
#     logger.info("got text message :", text)
#     # the first time you chat with the bot AKA the welcoming message
#     if text == "/start":
#         # print the welcoming message
#         bot_welcome = """
#        Welcome to Finy bot, the bot is using the service from http://avatars.adorable.io/ to generate cool
#        looking avatars based on the name you enter so please enter a name and the bot will
#        reply with an avatar for your name.
#        """
#         # send the welcoming message
#         bot.sendChatAction(chat_id=chat_id, action="typing")
#         sleep(1.5)
#         bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
#     else:
#         try:
#             # clear the message we got from any non alphabets
#             text = re.sub(r"\W", "_", text)
#             # create the api link for the avatar based on http://avatars.adorable.io/
#             url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
#             # reply with a photo to the name the user sent,
#             # note that you can send photos by url and telegram will fetch it for you
#             bot.sendChatAction(chat_id=chat_id, action="upload_photo")
#             sleep(2)
#             bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
#         except Exception:
#             # if things went wrong
#             bot.sendMessage(chat_id=chat_id,
#                             text="There was a problem in the name you used, please enter different name",
#                             reply_to_message_id=msg_id)
#
#     return 'ok'


# @app.route('/setwebhook', methods=['GET', 'POST'])
# def set_webhook():
#     # we use the bot object to link the bot to our app which live
#     # in the link provided by URL
#     s = bot.setWebhook('{URL}/{HOOK}'.format(URL=config.heroku_config.url, HOOK=config.heroku_config.url))
#     # something to let us know things work
#     if s:
#         return "webhook setup ok"
#     else:
#         return "webhook setup failed"

if __name__ == "__main__":
    PORT = 8000
    http_tunnel = ngrok.connect(PORT, bind_tls=True)
    public_url = http_tunnel.public_url
    HOST_URL = public_url

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(set_telegram_webhook_url())
    if success:
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info")
    else:
        print("Fail, closing the app.")
