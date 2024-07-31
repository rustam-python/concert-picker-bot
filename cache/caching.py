import datetime

import cache
import database as db


class Caching:
    @staticmethod
    @cache.redis_cache()
    def get_artist_id(name: str) -> int:
        return db.Artists.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_album_id(name: str) -> int:
        return db.Albums.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_track_id(name: str) -> int:
        return db.Tracks.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_scrobble_id(artist: str, album: str, track: str, scrobble_date: datetime.datetime) -> int:
        """
        Запрашивает Scrobble из кэша. Если в кэше нет, то смотрим в БД. Если в БД нет, то добавляем и туда, и туда.
        """
        return db.Scrobbles.add(artist=artist, album=album, track=track, scrobble_date=scrobble_date).id
