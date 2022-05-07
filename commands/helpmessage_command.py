async def main(client, logger, **kwargs):
    print(kwargs)
    response = """**Работающие команды**:
/join имя_канала, /add - добавить канал в текущий поток. Также можно переслать сюда сообщение из канала
/leave имя_канала, /remove - удалить канал из текущего потока
/list - показать список каналов, добавленных в поток
/stop, /pause - приостановить пересылку
/start, resume - продолжить пересылку
/filter слово - добавить стоп слово
/unfilter слово - удалить стоп слово
/clearfilter - очистить фильтр
/filterlist - список фильтров
/filterstop, /filterstart - отключить/включить фильтрацию
/help - список команд

**Команды в работе**:
/exit, /delete - удалить все каналы и остановить пересылку
/roll - показать случайный пост из каналов в потоке
/random - показать случайный пост из всех каналов (даже других пользователей)
/top - топ самых популярных каналов
/rare - топ самых редких каналов
/recommend - предлагает случайный канал"""
    # /log off/on - переключение режима логирования в отельный канал
    # /stat - статистика потоков, юзеров и каналов
    await client.send_message(kwargs['answer_to'], response)
