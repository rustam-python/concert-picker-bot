import asyncio
import collections.abc
import dataclasses
import datetime
import time

import aiohttp
import requests

import cache
import logger
import schemas
import sentry
import settings
from getters.errors import LastFMServerResponseError

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@dataclasses.dataclass
class Scrobble:
    album: str
    album_mbid: str
    artist: str
    artist_mbid: str
    date: datetime.datetime
    track: str
    track_mbid: str


@dataclasses.dataclass
class Page:
    number: int
    scrobbles: list[Scrobble] = dataclasses.field(default_factory=list)


class LastFMScrobbleDataGetter:

    def __init__(self):
        self._pages_for_retry = []
        self.logger = logger.Logger(name=self.__class__.__name__)

    def get_scrobbles(self):
        try:
            self.logger.info('Getting data...')
            start = time.time()
            self.logger.info('Start DB update...')
            for page in self._get_pages():
                for scrobble in page.scrobbles:
                    cache.Caching.get_scrobble_id(
                        track=scrobble.track,
                        artist=scrobble.artist,
                        album=scrobble.album,
                        scrobble_date=scrobble.date
                    )
            self.logger.success(f'DB update finished with {round(time.time() - start, 2)} seconds.')
        except Exception as e:
            sentry.capture_exception(e)
            self.logger.error(f'Error during getting data: {e}', stack_info=True)

    def _get_pages(self) -> list[Page]:
        self.logger.info('Getting scrobbles from LastFM...')
        max_page_number = self._get_total_pages_count()
        results = loop.run_until_complete(self._make_requests(range(1, max_page_number + 1)))
        if self._pages_for_retry:
            count = 5
            while count > 0:
                self.logger.info(f'Trying to reload failed pages. {count} tries left.')
                results += loop.run_until_complete(self._make_requests(self._pages_for_retry))
                count -= 1
        if self._pages_for_retry:
            self.logger.error('There are still not get pages!')
        self.logger.success('Getting info finished!')
        return [result for result in results if result is not None]

    def _get_total_pages_count(self):
        """
        This function gets total scrobbles pages count for downloading.
        """
        response = requests.get(
            f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=200&user={settings.APIs.lastfm_username}&api_key={settings.APIs.lastfm_token}&format=json'  # noqa: E501
        )
        if not response.ok:
            error_msg = self._get_response_error_message(response)
            raise LastFMServerResponseError(error_msg)
        data = schemas.ScrobbleData(**response.json())
        return int(data.recenttracks.attr.totalPages)

    def _get_response_error_message(self, response: requests.models.Response) -> str:
        """
        Tries to extract error message from Redfish
        service HTTP response and write it to log
        :param response: response where error message should be extracted from
        :return: nothing
        """
        error_msg = ''
        try:
            error_msg = response.json()
        except Exception as e:
            self.logger.failure(f'Failure on attempt to extract error data from response: {e}', stack_info=True)
        else:
            error_msg = f'Response error message: {error_msg}'
        return error_msg

    async def _make_requests(self, pages_numbers: collections.abc.Iterable):
        # Limit the number of connections to 10.
        connector = aiohttp.TCPConnector(limit=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for page_number in pages_numbers:
                url = f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=200&page={page_number}&user={settings.APIs.lastfm_username}&api_key={settings.APIs.lastfm_token}&format=json'  # noqa: E501
                try:
                    tasks.append(self._get_page_data(url=url, number=page_number, session=session))
                    if page_number in self._pages_for_retry:
                        self._pages_for_retry.remove(page_number)
                except Exception as e:
                    sentry.capture_exception(e)
                    self.logger.error(f'Failed to get LastFM data from {url}, error: {e}', stack_info=True)
                    if page_number not in self._pages_for_retry:
                        self._pages_for_retry.append(page_number)
            result = await asyncio.gather(*tasks)
        return result

    async def _get_page_data(self, url: str, number: int, session: aiohttp.ClientSession) -> Page:
        """
        This function gets data from single page.
        """
        data = await self._send_request(url=url, session=session)
        scrobbles = schemas.ScrobbleData(**data)
        page = Page(number)
        for scrobble in scrobbles.recenttracks.tracks:
            if scrobble.nowplaying:  # If track is playing now it has no scrobble date yet.
                continue
            page.scrobbles.append(
                Scrobble(
                    album=scrobble.album.text,
                    album_mbid=scrobble.album.mbid,
                    artist=scrobble.artist.text,
                    artist_mbid=scrobble.artist.mbid,
                    date=datetime.datetime.utcfromtimestamp(int(scrobble.date.uts)),
                    track=scrobble.name,
                    track_mbid=scrobble.mbid
                )
            )
        return page

    async def _send_request(self, url: str, session: aiohttp.ClientSession):
        response = await session.request(method="GET", url=url)
        if not response.ok:
            error = await response.json()
            self.logger.error(f'Error: {error}')
            raise LastFMServerResponseError(error)
        return await response.json()
