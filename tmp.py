import logging
from dataclasses import dataclass
from datetime import datetime
from time import time
from typing import List, Dict

import requests


class CustomFormatter(logging.Formatter):
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
        logging.DEBUG: italic + white + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold + red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger('Events parser')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)


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


def get_kudago_data(r_string: str) -> List[dict]:
    """
    It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.
    :param r_string: request URL
    :return: list of events data
    """
    r = requests.get(r_string)
    response = r.json()
    if not response.get('next'):
        return [response]
    return get_kudago_data(response.get('next')) + [response]


def process_request_data(response: List[dict]) -> List[Event]:
    logger.info('Processing events data...')
    data: List[Event] = []
    for _dict in response:
        for event in _dict['results']:
            try:
                data.append(Event(event_id=event.get('id'), date=event.get('dates'), title=event.get('title'),
                                  place=event.get('place'), slug=event.get('slug'), price=event.get('price')))
            except TypeError:
                logger.error(f'The data of event is corrupted: {event}')
    return data


def get_scrobbled_artists(user: str, token: str) -> List[str]:
    logger.info('Request LastFM API for scrobbled artists list...')
    response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={user}&period=overall&'
                            f'limit=300&api_key={token}&format=json')
    _json = response.json()
    data: List[str] = []
    for artist in _json['topartists']['artist']:
        data.append(artist['name'])
    return data


def events_filter(event_list: List[Event], artist_list: List[str]) -> List[Event]:
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


if __name__ == '__main__':
    logger.info('Work started.')
    r_str = f'https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&fields=id,dates,title,place,slug,price&' \
            f'expand=&order_by=&text_format=&ids=&location=msk&actual_since={time()}&actual_until=&' \
            f'is_free=&categories=concert'

    user = 'chemp86'
    token = 'cac6eb8ee3cad6ee8bfe406af4528217'
    events = events_filter(event_list=process_request_data(get_kudago_data(r_str)),
                           artist_list=get_scrobbled_artists(user, token))
    [print(event) for event in events]
