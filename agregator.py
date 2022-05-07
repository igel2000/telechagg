import os
import logging
from pprint import pp, pprint, pformat
import json
from datetime import date, datetime
import time
import json
from pathlib import Path, PurePath
import pickle

from dotenv import load_dotenv
from telethon import errors

import hashlib

#from telethon import TelegramClient, events

from telethon.sync import TelegramClient, events
#from telethon import connection

# классы для работы с каналами
#from telethon.tl.functions.channels import GetParticipantsRequest
#from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
#from telethon.tl.functions.messages import GetHistoryRequest

class DateTimeEncoder(json.JSONEncoder):
    '''Класс для сериализации записи дат в JSON'''
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)

async def send_read(chat, message):
    try:
        chat_read = await client.get_input_entity(chat)
        await client.send_read_acknowledge(chat_read, message)
    except Exception as e:
        #logger.error(e)
        print(e)

load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
master_account = os.getenv("MASTER_ACCOUNT")
bot_token = os.getenv("BOT_TOKEN")
#urls = os.getenv("URLS").split(",")
forwarded_messages_filename = os.getenv("FORWARDED_MESSAGES_FILENAME")


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("tggt")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("app.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

client = TelegramClient('telegregator_session', api_id, api_hash)
client.start()

forwarded_messages = []
if Path(PurePath(forwarded_messages_filename)).exists():
    with open(forwarded_messages_filename, 'rb') as f:
        forwarded_messages = pickle.load(f)    

# обработать непрочитанные сообщения
dlgs = client.get_dialogs()
chats = [[d.unread_count, d.title] for d in dlgs if not getattr(d.entity, 'is_private', False) and d.unread_count != 0]
for chat in chats:
    pprint(chat)
    #if chat[1] != "338":
    #    print("skipped...")
    #    continue
    messages = client.get_messages(chat[1], chat[0])
    for message in messages:
        sha = hashlib.sha1(message.message.encode('utf-8')).hexdigest()
        message_info = {'message': message.__dict__, 'message_hash': sha}
        logger.info(pformat(message_info))
        if next((x for x in forwarded_messages if x == message_info["message_hash"]), None) is None:
            logger.info(f'Сообщение {message_info["message_hash"]} ранее не отправлялось')
            while True:
                try:
                    if message._chat is not None:
                        client.forward_messages(1532368226, message.id, message._chat)
                        message.mark_read()
                        forwarded_messages.append(message_info["message_hash"])
                        with open(forwarded_messages_filename, 'wb') as f:
                            pickle.dump(forwarded_messages, f)                           
                    break
                except errors.FloodWaitError as e:                    
                    print('Have to sleep', e.seconds, 'seconds')
                    time.sleep(e.seconds)
        else:
            logger.info(f'Сообщение {message_info["message_hash"]} ранее уже отправлялось')
            while True:
                try:
                    message.mark_read()
                    break
                except errors.FloodWaitError as e:                    
                    print('Have to sleep', e.seconds, 'seconds')
                    time.sleep(e.seconds)

# повесить обработчик на новые сообщения
@client.on(events.NewMessage)
async def my_event_handler(event):
    event_info = {"event": event.__dict__}
    if event._input_chat is not None:
        event_info["event._input_chat"] = event._input_chat.__dict__
    if event._chat is not None:
        event_info["event._chat"] = event._chat.__dict__
    if event._chat_peer is not None:
        event_info["event._chat_peer"] = event._chat_peer.__dict__
    if event.message is not None:
        event_info["event.message"] = event.message.__dict__
    if event.message._chat is not None:
        event_info["event.message._chat"] = event.message._chat.__dict__
    if event.message._chat_peer is not None:
        event_info["event.message._chat_peer"] = event.message._chat_peer.__dict__
    event_info["event.message_hash"] = hashlib.sha1(event.message.message.encode('utf-8')).hexdigest()

    logger.info(pformat(event_info))
    if next((x for x in forwarded_messages if x == event_info["event.message_hash"]), None) is None:
        logger.info(f'Сообщение {event_info["event.message_hash"]} ранее не отправлялось')
        while True:
            try:
                if event.message._chat is not None:
                    await client.forward_messages(1532368226, event.message.id, event.message._chat)
                    await event.mark_read()
                    forwarded_messages.append(event_info["event.message_hash"])
                    with open(forwarded_messages_filename, 'wb') as f:
                        pickle.dump(forwarded_messages, f)                           
                break
            except errors.FloodWaitError as e:                    
                print('Have to sleep', e.seconds, 'seconds')
                time.sleep(e.seconds)
    else:
        logger.info(f'Сообщение {event_info["event.message_hash"]} ранее уже отправлялось')
        while True:
            try:
                await event.mark_read()
                break
            except errors.FloodWaitError as e:                    
                print('Have to sleep', e.seconds, 'seconds')
                time.sleep(e.seconds)

client.run_until_disconnected()




