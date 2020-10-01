from dataclasses import dataclass
from datetime import datetime
from logging import Formatter, CRITICAL, ERROR, WARNING, INFO, DEBUG, StreamHandler, getLogger
from typing import List, Dict

import requests


class CustomFormatter(Formatter):
    """Logging Formatter to add colors"""
    bold = '\x1b[1m'
    italic = '\x1b[3m'
    underline = '\x1b[4m'
    reverse_video = '\x1b[7m'
    crossed_out = '\x1b[9m'

    red = '\x1b[31m'
    green = '\x1b[32m'
    yellow = '\x1b[33m'
    blue = '\x1b[34m'
    magenta = '\x1b[35m'
    cyan = '\x1b[36m'
    white = '\x1b[37m'
    black = '\x1b[30m'

    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        DEBUG: italic + white + format + reset,
        INFO: cyan + format + reset,
        WARNING: yellow + format + reset,
        ERROR: red + format + reset,
        CRITICAL: bold + red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


class Processor:
    """Dummy manager class."""
    pass


class MessageSender:
    """Dummy class for work with Telegram API."""
    def send(self):
        pass


class EventsRetriever:
    def get_events(self):
        pass


@dataclass
class Event:
    event_id: int
    place: List[Dict[str, int]]
    price: str
    slug: str
    title: str
    date: List[Dict[str, datetime]]

    def __str__(self):
        return f'event_id={self.event_id}, place={self.place}, price={self.price}, slug={self.slug}, ' \
               f'title={self.title}, date={self.date}'


class EventsCreator:
    def _get_kudago_data(self, r_string: str) -> List[dict]:
        """
        It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.
        :param r_string: request URL
        :return: list of events data
        """

        r = requests.get(r_string)
        response = r.json()
        if not response.get('next'):
            return [response]
        return self._get_kudago_data(response.get('next')) + [response]

    def _events_factory(self, response: List[dict]) -> List[Event]:
        logger.info('Processing events data...')
        events: List[Event] = []
        for _dict in response:
            for event in _dict['results']:
                try:
                    events.append(Event(event_id=event.get('id'), date=event.get('dates'), title=event.get('title'),
                                        place=event.get('place'), slug=event.get('slug'), price=event.get('price')))
                except TypeError:
                    logger.error(f'The data of event is corrupted: {event}')
        return events


class SQLProcessor:
    """Dummy class for work with DB."""

    def __init__(self):
        pass

    def __call__(self, events: List[Event]):
        pass

    def _get_events(self):
        pass

    def _write_to_sql(self):
        pass


if __name__ == '__main__':
    logger = getLogger('Events parser')
    logger.setLevel(INFO)
    console_handler = StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
