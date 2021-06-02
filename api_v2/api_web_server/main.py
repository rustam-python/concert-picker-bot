from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pprint
from time import time
from typing import List, Dict, Optional

import requests
from pydantic import ValidationError

import database
import pydantic_models
from api_v2.api_web_server import settings
from api_v2.api_web_server.error import LastFMResponseError, KudaGoResponseError
from api_v2.api_web_server.logging_utils import get_logger

logger = get_logger('Events Getter')


class MessageSender:
    """Dummy class for work with Telegram API."""

    def send(self):
        pass


# noinspection PyMethodMayBeStatic
class EventsProcessor:
    """
    This class returns the list of Events.
    """

    def __init__(self):
        pass

    def get_events_list(self, url: str, username: str, token: str) -> List[pydantic_models.Event]:
        try:
            return self._events_filter(event_list=self._get_kudago_data(url),
                                       artist_list=self._get_scrobbled_artists(username, token))
        except Exception as e:
            logger.critical(e)

    def _get_kudago_data(self, url: str, counter: int = 1) -> List[pydantic_models.Event]:
        """
        It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.
        :param url: request URL
        :return: list of events data
        """
        logger.info(f'Request KudaGo API for list of concerts - page {counter}...')
        response = requests.get(url)
        if not response.ok:
            error = ''
            try:
                error = response.json().get('detail')
            except Exception as err:
                logger.critical(err)
            message = f'KudaGo API is returned an error - {error}'
            logger.critical(message)
            raise KudaGoResponseError(message)

        try:
            kudago = pydantic_models.KudaGoEvents(**response.json())
        except ValidationError as e:
            raise KudaGoResponseError(f'KudaGo API returned wrong data:\n{e.json()}')

        if not kudago.next:
            return kudago.results
        counter += 1
        return self._get_kudago_data(kudago.next, counter) + kudago.results

    def _get_scrobbled_artists(self, username: str, token: str, artists_limit: int = 300) -> List[str]:
        """
        This method requests API of LastFM for a list of 200 popular artists of the user.
        :param username: LastFM user
        :token: LastFM API token
        :return: list of artists
        """
        logger.info('Request LastFM API for scrobbled artists list...')
        response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&'
                                f'period=overall&limit={artists_limit}&api_key={token}&format=json')
        if not response.ok:
            error = ''
            try:
                error = response.json().get('message')
            except Exception as err:
                logger.critical(err)
            message = f'LastFM API is returned an error - {error}'
            logger.critical(message)
            raise LastFMResponseError(message)
        try:
            lastfm = pydantic_models.LastFMResponse(**response.json())
        except ValidationError as e:
            raise LastFMResponseError(f'LastFM API returned wrong data:\n{e.json()}')

        data: List[str] = []
        for artist in lastfm.topartists.artist:
            data.append(artist.name)
        return data

    def _events_filter(self,
                       event_list: List[pydantic_models.Event], artist_list: List[str]) \
            -> List[pydantic_models.Event]:
        """
        The function filters passed Events list by the passed list of artists.
        :param event_list: events data from KudaGo API.
        :param artist_list: scrobbled artists data from LastFM API.
        :return: filtered by artist events data
        """
        logger.info('Filter events...')
        data: List[pydantic_models.Event] = []
        for event in event_list:
            for artist in artist_list:
                if artist in event.title:
                    data.append(event)
        return data


# class PlacesExtractor:
#     def __init__(self, events: List[Event]):
#         self._events: List[Event] = events
#
#     def _places_extractor(self):
#         self._events


# class SQLProcessor:
#     """Dummy class for work with DB."""
#
#     def __init__(self):
#         pass
#
#     def __call__(self, events: List[Event]):
#         pass
#
#     def _get_events(self):
#         return database.Events.select()
#
#     def _write_to_sql(self):
#         pass


# def process_event(event: Event):
#     # Create dates of event.
#     dates = [database.Dates.add(start=date['start'], end=date['end']) for date in event.date]
#     # Create dates of event.
#     database.Places()
#     _event = database.Events.add(event.event_id, event.title, event.place.get('id'), event.slug, event.price)
#     for date in dates:
#         database.EventsInDates.add(event_id=_event.event_id, dates_id=date.id)


def place_getter(place_id: int):
    result = requests.get(
        f'https://kudago.com/public-api/v1.4/places/{place_id}/?lang=&fields=id,title,address&location=msk'
    )
    results = result.json()
    return results


# noinspection PyMethodMayBeStatic
class PlacesProcessor:
    def __init__(self):
        pass

    def process(self):
        pass

    def _get_kudago_place(self, place_id: int) -> pydantic_models.KudaGoPlace:
        url = f'https://kudago.com/public-api/v1.4/places/{place_id}/?lang=&fields=id,title,address&location=msk'
        response = requests.get(url)
        if not response.ok:
            error = ''
            try:
                error = response.json().get('detail')
            except Exception as err:
                logger.critical(err)
            message = f'KudaGo API is returned an error - {error}'
            logger.critical(message)
            raise KudaGoResponseError(message)

        try:
            kudago = pydantic_models.KudaGoPlace(**response.json())
        except ValidationError as e:
            raise KudaGoResponseError(f'KudaGo API returned wrong data:\n{e.json()}')
        return kudago


if __name__ == '__main__':
    url = f'https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&fields=id,dates,title,place,slug,price&' \
          f'expand=&order_by=&text_format=&ids=&location=msk&actual_since={time()}&actual_until=&is_free=&' \
          f'categories=concert'

    print(PlacesProcessor()._get_kudago_place(359))

    # getter = EventsProcessor()
    # events: List[pydantic_models.Event] = getter.get_events_list(url=url,
    #                                                              username=settings.Server.username,
    #                                                              token=settings.Server.last_fm_api_key)
    # database.initialize_data_base()

    # write events to SQL
    # database.Places.bunch_insert([(event.place.id, None, None) for event in events])
