import dataclasses
import datetime


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
