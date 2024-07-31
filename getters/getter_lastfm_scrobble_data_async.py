import collections.abc
import datetime
import time

import requests

import cache
import logger
import schemas
import sentry
import settings
from getters.errors import LastFMResponseError
from getters._dataclasses import Page, Scrobble


class GetterLastFMScrobbleDataAsync:

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
        results = self._make_requests(range(1, max_page_number + 1))
        if self._pages_for_retry:
            count = 5
            while count > 0:
                self.logger.info(f'Trying to reload failed pages. {count} tries left.')
                results += self._make_requests(self._pages_for_retry)
                count -= 1
        if self._pages_for_retry:
            self.logger.error('There are still not get pages!')
        self.logger.success('Getting info finished!')
        return [result for result in results if result is not None]

    def _get_total_pages_count(self):
        """Gets the total number of pages to download with scrobbling from the first page of the scrobbling request."""
        response = requests.get(
            settings.APIs.url_recent_tracks.format(
                user=settings.APIs.lastfm_username,
                api_key=settings.APIs.api_key
            )
        )
        if not response.ok:
            error_msg = self._get_response_error_message(response)
            raise LastFMResponseError(error_msg)
        data = schemas.ScrobbleData(**response.json())
        return int(data.recenttracks.attr.totalPages)

    def _get_response_error_message(self, response: requests.models.Response) -> str:
        error_msg = ''
        try:
            error_msg = response.json()
        except Exception as e:
            self.logger.failure(f'Failure on attempt to extract error data from response: {e}', stack_info=True)
        else:
            error_msg = f'Response error message: {error_msg}'
        return error_msg

    def _make_requests(self, pages_numbers: collections.abc.Iterable):
        results = []
        for page_number in pages_numbers:
            url = settings.APIs.url_recent_tracks_via_page.format(
                page=page_number,
                user=settings.APIs.lastfm_username,
                api_key=settings.APIs.api_key
            )
            try:
                result = self._get_page_data(url=url, number=page_number)
                if page_number in self._pages_for_retry:
                    self._pages_for_retry.remove(page_number)
                results.append(result)
            except Exception as e:
                sentry.capture_exception(e)
                self.logger.error(f'Failed to get LastFM data from {url}, error: {e}', stack_info=True)
                if page_number not in self._pages_for_retry:
                    self._pages_for_retry.append(page_number)
        return results

    def _get_page_data(self, url: str, number: int) -> Page:
        """
        This function gets data from single page.
        """
        data = self._send_request(url=url)
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

    def _send_request(self, url: str):
        response = requests.get(url)
        if not response.ok:
            error = response.json()
            self.logger.error(f'Error: {error}')
            raise LastFMResponseError(error)
        return response.json()
