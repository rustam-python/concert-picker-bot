import datetime

import cache
import database


class Caching:
    @staticmethod
    @cache.redis_cache()
    def get_artist_id(name: str) -> int:
        return database.Artist.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_album_id(name: str) -> int:
        return database.Album.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_track_id(name: str) -> int:
        return database.Track.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_scrobble_id(artist: str, album: str, track: str, scrobble_date: datetime.datetime) -> int:
        return database.Scrobble.add(artist=artist, album=album, track=track, scrobble_date=scrobble_date).id


