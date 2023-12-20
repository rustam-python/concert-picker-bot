import abc
import datetime
import time

import requests

import database as db
import logger
import schemas
import sentry
import settings
from getters.errors import LastFMResponseError, KudagoResponseError


class _ProtoGetter:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    @abc.abstractmethod
    def get_data(self):
        pass


# noinspection PyBroadException
class GetterEvents(_ProtoGetter):
    """This class returns the list of Events."""

    def get_data(self) -> list[schemas.Event] | None:
        events_list = None
        try:
            kudago_url = settings.APIs.kudago_url.format(time.time())
            events = self._get_kudago_data(kudago_url)
            artists = self._get_scrobbled_artists()
            events_list = self._get_events(events=events, artists=artists)
        except Exception as e:
            sentry.capture_exception(e)
            self.logger.error(f"Failed to get data from API's: {e}", stack_info=True)
            db.Log.add(datetime.datetime.now(), "Failed to get data from API's", 'error')
        return events_list

    def _get_kudago_data(self, url: str, counter: int = 1) -> list[schemas.Event]:
        """
        It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.

        :param url: request URL
        :return: list of events data
        """
        self.logger.info(f'Request KudaGo API for list of concerts - page {counter}')
        response = requests.get(url)
        if not response.ok:
            error = response.json().get('detail')
            message = f'Failed to get KudaGo data: {error}'
            self.logger.error(message)
            raise KudagoResponseError(message)
        kudago = schemas.EventsList(**response.json())
        if not kudago.next:
            return kudago.results
        counter += 1
        return self._get_kudago_data(kudago.next, counter) + kudago.results

    def _get_scrobbled_artists(self) -> list[str]:
        """
        This method requests API of LastFM for a list of 200 popular artists of the user.

        :return: list of artists
        """
        self.logger.info('Request LastFM API for scrobbled artists list')
        try:
            response = requests.get(
                url=settings.APIs.lastfm_url.format(
                    settings.APIs.lastfm_username,
                    settings.APIs.lastfm_artists_limit,
                    settings.APIs.lastfm_token
                ),
                timeout=20
            )
        except Exception as e:
            self.logger.error('Failed to get LastFM data')
            raise e
        if not response.ok:
            error = response.json().get('message')
            message = f'Failed to get LastFM data: {error}'
            raise LastFMResponseError(message)
        lastfm = schemas.Artists(**response.json())
        data = [artist.name for artist in lastfm.topartists.artist]
        return data

    def _get_events(self, events: list[schemas.Event], artists: list[str]) -> list[schemas.Event]:
        """
        The function filters passed Events list by the passed list of artists.

        :param events: events data from KudaGo API.
        :param artists: scrobbled artists data from LastFM API.
        :return: filtered by artist events data
        """
        self.logger.info('Search for required artists in Events list')
        data: list[schemas.Event] = []
        for event in events:
            for artist in artists:
                if artist in event.title and event not in data:
                    data.append(event)
        return data
