from dataclasses import dataclass
from datetime import datetime
from logging import Formatter, CRITICAL, ERROR, WARNING, INFO, DEBUG, StreamHandler, getLogger
from time import time
from typing import List, Dict

import requests
from .model import initialize_data_base, Events
from .settings import Server


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
    def __init__(self, user: str, token: str):
        self.r_str = f'https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&' \
                     f'fields=id,dates,title,place,slug,price&expand=&order_by=&text_format=&ids=&location=msk&' \
                     f'actual_since={time()}&actual_until=&is_free=&categories=concert'
        self.username = user
        self.token = token

    def __call__(self) -> List[Event]:
        return self._events_filter(event_list=self._events_factory(self._get_kudago_data(self.r_str)),
                                   artist_list=self._get_scrobbled_artists(self.username, self.token))

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

    def _get_scrobbled_artists(self, username: str, token: str) -> List[str]:
        """
        This method requests API of LastFM for a list of 200 popular artists of the user.
        :param username: LastFM user
        :token: LastFM API token
        :return: list of artists
        """
        logger.info('Request LastFM API for scrobbled artists list...')
        response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&'
                                f'period=overall&limit=300&api_key={token}&format=json')
        _json = response.json()
        data: List[str] = []
        for artist in _json['topartists']['artist']:
            data.append(artist['name'])
        return data

    def _events_filter(self, event_list: List[Event], artist_list: List[str]) -> List[Event]:
        """
        The function filters passed Events list by the passed list of artists.
        :param event_list: events data from KudaGo API.
        :param artist_list: scrobbled artists data from LastFM API.
        :return: filtered by artist events data
        """
        logger.info('Filter events...')
        data: List[Event] = []
        for event in event_list:
            for artist in artist_list:
                if artist in event.title:
                    data.append(event)
        return data


class SQLProcessor:
    """Dummy class for work with DB."""

    def __init__(self):
        pass

    def __call__(self, events: List[Event]):
        pass

    def _get_events(self):
        return Events.select()

    def _write_to_sql(self):
        pass


if __name__ == '__main__':
    logger = getLogger('Events parser')
    logger.setLevel(INFO)
    console_handler = StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
