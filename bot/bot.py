import datetime
import time
import typing

import peewee
import pydantic
import pytz
import telebot

import database
import logger
import parsers
import settings


class _Event(pydantic.BaseModel):
    event_id: int
    title: str
    place_name: str
    place_address: str
    date_start: datetime.datetime
    date_stop: datetime.datetime
    price: str


# noinspection PyBroadException
class Bot:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    def start(self):
        bot = telebot.TeleBot(settings.APIs.telegram_token)
        while True:
            parser = parsers.ParserApi()
            if parser.proc():
                events = self._get_events()
                if events:
                    self._send_messages(bot=bot, events=events)
            time.sleep(settings.App.delay_time)

    def _get_events(self) -> typing.List[_Event]:
        result = None
        try:
            query = (
                database.Events.select(database.Events.event_id,
                                       database.Events.title,
                                       database.Place.title.alias('place_name'),
                                       database.Place.address.alias('place_address'),
                                       database.EventDates.date_start,
                                       database.EventDates.date_stop,
                                       database.Events.price).
                    join(database.Place).switch(database.Events).
                    join(database.EventDates, join_type=peewee.JOIN.LEFT_OUTER).
                    where(database.Events.is_sent != True).
                    dicts().
                    execute()
            )
            events = [event for event in query]
            result = [_Event(**data) for data in events]
        except Exception:
            self.logger.critical('Error occurred during events DB request', stack_info=True)
        return result

    def _send_messages(self, bot: telebot.TeleBot, events: typing.List[_Event]):
        tz = pytz.timezone('Europe/Moscow')
        sent_ids = []
        for i, event in enumerate(events, start=1):
            try:
                message = (
                    f'{i}. *{event.title}*:\n\n'
                    f'_Дата_: {event.date_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=tz).strftime("%d.%m.%Y %H:%M")};\n\n'
                    f'_Место_: {event.place_name} ({event.place_address});\n\n'
                    f'_Билеты_: {event.price}.'
                )
                bot.send_message(chat_id=settings.APIs.telegram_chat_id,
                                 text=f'\U0001F3B8 *Новые концерты*\n\n{message}',
                                 parse_mode='Markdown')
                sent_ids.append(event.event_id)
                self.logger.success('Message was successfully sent')
            except Exception:
                self.logger.critical('Error occurred during message sending', stack_info=True)
        try:
            database.Events.update(is_sent=True).where(database.Events.event_id.in_(sent_ids)).execute()
        except Exception:
            self.logger.critical('Error occurred during marking events as sent', stack_info=True)
