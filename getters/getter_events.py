import abc
import datetime
import time
import typing

import pydantic
import requests

import logger
import settings
from getters.errors import LastfmError, KudagoError


class _Place(pydantic.BaseModel):
    id: int


class _Dates(pydantic.BaseModel):
    start: datetime.datetime
    end: datetime.datetime


class Event(pydantic.BaseModel):
    id: int
    dates: typing.List[_Dates]
    title: str
    slug: str
    place: typing.Optional[_Place]
    price: str


class _Events(pydantic.BaseModel):
    count: int
    next: typing.Optional[str]
    previous: typing.Optional[str]
    results: typing.List[Event]


class _TopArtistsAttr(pydantic.BaseModel):
    page: str
    perPage: str
    total: str
    totalPages: str
    user: str


class _ArtistsAttr(pydantic.BaseModel):
    rank: str


class _Image(pydantic.BaseModel):
    _text: str
    size: str

    class Config:
        fields = {
            '_text': '#text'
        }


class _Artist(pydantic.BaseModel):
    _attr: _ArtistsAttr
    image: pydantic.conlist(_Image, min_items=5, max_items=5)
    mbid: str
    name: str
    playcount: str
    streamable: str
    url: str

    class Config:
        fields = {
            '_attr': '@attr'
        }


class _TopArtists(pydantic.BaseModel):
    _attr: _TopArtistsAttr
    artist: typing.List[_Artist]

    class Config:
        fields = {
            '_attr': '@attr'
        }


class _Artists(pydantic.BaseModel):
    topartists: _TopArtists


class _ProtoGetter:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    @abc.abstractmethod
    def get(self):
        pass


# noinspection PyBroadException
class GetterEvents(_ProtoGetter):
    """
    This class returns the list of Events.
    """

    def get(self) -> typing.Optional[typing.List[Event]]:
        result = None
        try:
            kudago_url = settings.APIs.kudago_url.format(time.time())
            events = self._get_kudago_data(kudago_url)
            artists = self._get_scrobbled_artists()
            result = self._get_events(events=events, artists=artists)
        except Exception:
            self.logger.critical('Failed to get events from KudaGo', stack_info=True)
        return result

    def _get_kudago_data(self, url: str, counter: int = 1) -> typing.List[Event]:
        """
        It is a recursive function that takes the URL of the request to the KudaGo API and return data of events.
        :param url: request URL
        :return: list of events data
        """
        self.logger.info(f'Request KudaGo API for list of concerts - page {counter}')
        response = requests.get(url)
        if not response.ok:
            error = response.json().get('detail')
            self.logger.error(f'Failed to get KudaGo data: {error}')
            raise KudagoError
        kudago = _Events(**response.json())
        if not kudago.next:
            return kudago.results
        counter += 1
        return self._get_kudago_data(kudago.next, counter) + kudago.results

    def _get_scrobbled_artists(self) -> typing.List[str]:
        """
        This method requests API of LastFM for a list of 200 popular artists of the user.
        :return: list of artists
        """
        self.logger.info('Request LastFM API for scrobbled artists list')
        response = requests.get(
            settings.APIs.lastfm_url.format(
                settings.APIs.lastfm_username,
                settings.APIs.lastfm_artists_limit,
                settings.APIs.lastfm_token
            )
        )
        if not response.ok:
            error = response.json().get('message')
            self.logger.critical(f'Failed to get LastFM data: {error}')
            raise LastfmError
        lastfm = _Artists(**response.json())
        data = [artist.name for artist in lastfm.topartists.artist]
        return data

    def _get_events(self, events: typing.List[Event], artists: typing.List[str]) -> typing.List[Event]:
        """
        The function filters passed Events list by the passed list of artists.
        :param events: events data from KudaGo API.
        :param artists: scrobbled artists data from LastFM API.
        :return: filtered by artist events data
        """
        self.logger.info('Search for required artists in Events list')
        data: typing.List[Event] = []
        for event in events:
            for artist in artists:
                if artist in event.title and event not in data:
                    data.append(event)
        return data
