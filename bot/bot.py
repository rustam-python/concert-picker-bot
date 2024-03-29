import datetime
import typing

import peewee
import pydantic
import pytz
import telebot

import database as db
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
    updated: bool


# noinspection PyBroadException
class Bot:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    def start(self):
        bot = telebot.TeleBot(settings.APIs.telegram_token)
        parser = parsers.ParserApi()
        if parser.start():
            events = self._get_events()
            if events:
                self._send_messages(bot=bot, events=events)
        bot.stop_bot()

    def _get_events(self) -> typing.Optional[list[_Event]]:
        result = None
        try:
            query = (
                db.Events.
                select(
                    db.Events.event_id,
                    db.Events.title,
                    db.Places.title.alias('place_name'),
                    db.Places.address.alias('place_address'),
                    db.EventDates.date_start,
                    db.EventDates.date_stop,
                    db.Events.price,
                    db.Events.updated
                ).
                join(db.Places).switch(db.Events).
                join(db.EventDates, join_type=peewee.JOIN.LEFT_OUTER).
                where(db.Events.is_sent != True).
                dicts().
                execute()
            )
            events = [event for event in query]
            result = [_Event(**data) for data in events]
        except Exception:
            self.logger.failure('Error occurred during events DB request', stack_info=True)
            db.Log.add(datetime.datetime.now(), 'Error occurred during events DB request', 'critical')
        return result

    def _send_messages(self, bot: telebot.TeleBot, events: list[_Event]):
        tz = pytz.timezone('Europe/Moscow')
        sent_ids = []
        for i, event in enumerate(events, start=1):
            date = event.date_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=tz).strftime("%d.%m.%Y %H:%M")
            try:
                message = (
                    f'{i}. *{event.title}*{"(_Обновлённая информация_)" if event.updated else ""}:\n\n'
                    f'_Дата_: {date};\n\n'
                    f'_Место_: {event.place_name} ({event.place_address});\n\n'
                    f'_Билеты_: {event.price}.'
                )
                bot.send_message(
                    chat_id=settings.APIs.telegram_chat_id,
                    text=f'\U0001F3B8 *Новые концерты*\n\n{message}',
                    parse_mode='Markdown'
                )
                sent_ids.append(event.event_id)
                self.logger.success('Message was successfully sent')
            except Exception:
                self.logger.failure('Error occurred during message sending', stack_info=True)
                db.Log.add(datetime.datetime.now(), 'Error occurred during message sending', 'critical')
        try:
            db.Events.update(is_sent=True).where(db.Events.event_id.in_(sent_ids)).execute()
        except Exception:
            self.logger.failure('Error occurred during marking events as sent', stack_info=True)
            db.Log.add(datetime.datetime.now(), 'Error occurred during marking events as sent', 'critical')
