from database import *

async def main(client, logger, **kwargs):
    # print(kwargs)
    chat = kwargs['answer_to']

    feed_id = chat.chat_id
    feedupdate = Feed.update({Feed.is_filter: 0}).where(Feed.feed_id == feed_id).execute()
    response = 'Выключили фильтрацию'

    await client.send_message(chat, response)
    logger.info(response)
