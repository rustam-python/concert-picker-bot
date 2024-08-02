import datetime
import pickle
import time

import requests

import database as db
import logger
import schemas
import sentry
import settings
from getters.errors import LastFMResponseError, KudagoResponseError


# noinspection PyBroadException
class ConcertsGetter:
    """This class returns the list of Events."""

    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    def get_data(self) -> list[schemas.Event] | None:
        events_list = None
        kudago_url = settings.APIs.kudago_url.format(time.time())
        try:
            events = self._get_kudago_data(kudago_url)
            artists = self._get_scrobbled_artists()
            events_list = self._get_events(events=events, artists=artists)

            # Сохранили объект на диск.
            with open('data.pickle', 'wb') as f:
                pickle.dump(events, f)

        except Exception as e:
            sentry.capture_exception(e)
            self.logger.error(f"Failed to get event\'s data -- {e}", stack_info=True)
            db.Log.add(datetime.datetime.now(), 'Failed to get event\'s data', 'error')
        return events_list

    def _get_kudago_data(self, url: str, page_number: int = 1) -> list[schemas.Event]:
        """
        It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.

        :param url: request URL
        :return: list of events data
        """
        self.logger.info(f'Request KudaGo API for list of concerts - page {page_number}')
        response = requests.get(url)
        if not response.ok:
            error = response.json().get('detail')
            raise KudagoResponseError(f'Failed to get KudaGo data: {error}')
        events = schemas.EventsList(**response.json())
        if not events.next:
            return events.results
        page_number += 1
        return self._get_kudago_data(events.next, page_number) + events.results

    def _get_scrobbled_artists(self) -> list[str]:
        """
        This method requests API of LastFM for a list of 200 popular artists of the user.

        :return: list of artists
        """
        self.logger.info('Request LastFM API for scrobbled artists list')

        url = settings.APIs.url_top_artists.format(
            user=settings.APIs.lastfm_username,
            limit=settings.APIs.lastfm_artists_limit,
            api_key=settings.APIs.api_key
        )
        response = requests.get(url=url, timeout=20)
        if not response.ok:
            error = response.json().get('message')
            raise LastFMResponseError(f'Failed to get LastFM data: {error}')
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
                if (artist.upper() in event.title.upper() or artist.upper() in event.slug.upper()) and event not in data:
                    data.append(event)
        return data
