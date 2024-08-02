import datetime
import pickle
import random
import time

import requests

import cache
import database as db
import logger
import schemas
import sentry
import settings
from getters._dataclasses import Page, Scrobble
from getters.errors import LastFMResponseError


class GetterScrobbleDataSync:

    def __init__(self):
        self._failed_pages = []
        self.logger = logger.Logger(name=self.__class__.__name__)

    def get_scrobbles(self):
        try:
            self.logger.info('Getting data...')
            start = time.time()
            self.logger.info('Start DB update...')
            pages = self._get_scrobble_pages()

            # Прочитали объект с диска.
            # with open('data.pickle', 'rb') as f:
            #     pages = pickle.load(f)

            last_processed_page = db.ProcessedPages.get_by_id(1)
            for page in pages:  # TODO: переделать механизм записи в БД -- сейчас все скробблы сначала собираются в один огромный список, который потом обрабатывается разом.
                for scrobble in page.scrobbles:
                    cache.Caching.get_scrobble_id(
                        track=scrobble.track,
                        artist=scrobble.artist,
                        album=scrobble.album,
                        scrobble_date=scrobble.date
                    )
                last_processed_page.last_processed_page += 1
                last_processed_page.save()
            self.logger.success(f'DB update finished with {round(time.time() - start, 2)} seconds.')
        except Exception as e:
            sentry.capture_exception(e)
            self.logger.error(f'Error during getting data: {e}', stack_info=True)

    def _get_scrobble_pages(self) -> list[Page]:
        self.logger.info('Getting scrobbles from LastFM...')
        total_pages_count = self._get_total_pages_count()
        results = []
        last_processed_page = db.ProcessedPages.get_by_id(1).last_processed_page
        for page_number in range(last_processed_page, total_pages_count + 1):
            # LastFM имеет неявное ограничение на количество запросов в промежуток времени. Точное значение неизвестно.
            timeout = random.randint(1, 10)
            self.logger.info(
                f'Getting {page_number} of {total_pages_count} scrobbles from LastFM... (timeout is {timeout})'
            )
            time.sleep(timeout)

            results.append(self._get_scrobble_page(page_number))
        if self._failed_pages:
            for page_number in self._failed_pages:
                count = 5
                while count > 0:
                    self.logger.info(f'Trying to reload failed pages. {count} tries left.')
                    results += self._get_scrobble_page(
                        page_number)  # TODO: переделать на нормальный механизм ретраев без уменьшения list, хранящегося в поле self._failed_pages
                    count -= 1
        if self._failed_pages:
            self.logger.error('There are still not get pages!')
        self.logger.success('Getting info finished!')
        return [result for result in results if result is not None]

    def _get_scrobble_page(self, page_number: int) -> None | Page:
        """
        Получает страницу с прослушиваниями.
        """
        url = settings.APIs.url_recent_tracks_via_page.format(
            page=page_number,
            user=settings.APIs.lastfm_username,
            api_key=settings.APIs.api_key
        )
        try:
            page = self._get_page_data(url=url, number=page_number)
            if page_number in self._failed_pages:
                self._failed_pages.remove(page_number)
            return page
        except Exception as e:
            sentry.capture_exception(e)
            self.logger.error(f'Failed to get LastFM data from {url}, error: {e}', stack_info=True)
            if page_number not in self._failed_pages:
                self._failed_pages.append(page_number)
                return

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

    def _get_page_data(self, url: str, number: int) -> Page:
        """
        This function gets data from single page.
        """
        response = requests.get(url)
        if not response.ok:
            error = response.json()
            self.logger.error(f'Error: {error}')
            raise LastFMResponseError(error)
        scrobbles = schemas.ScrobbleData(**response.json())
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


if __name__ == '__main__':
    db.initialize_data_base(is_local=False)
    GetterScrobbleDataSync().get_scrobbles()
