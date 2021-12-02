import datetime

import cache
import database


class Caching:
    @staticmethod
    @cache.redis_cache()
    def get_artist_id(name: str) -> int:
        return database.Artists.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_album_id(name: str) -> int:
        return database.Albums.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_track_id(name: str) -> int:
        return database.Tracks.add(name=name).id

    @staticmethod
    @cache.redis_cache()
    def get_scrobble_id(artist: str, album: str, track: str, scrobble_date: datetime.datetime) -> int:
        return database.Scrobbles.add(artist=artist, album=album, track=track, scrobble_date=scrobble_date).id


