import typing

import pydantic


class _ProtoElement(pydantic.BaseModel):
    mbid: str
    text: str = pydantic.Field(..., alias='#text')


class Artist(_ProtoElement):
    pass


class Album(_ProtoElement):
    pass


class Image(pydantic.BaseModel):
    size: str
    text: str = pydantic.Field(..., alias='#text')


class _Attr(pydantic.BaseModel):
    nowplaying: str


class Date(pydantic.BaseModel):
    uts: str
    text: str = pydantic.Field(..., alias='#text')


class Track(pydantic.BaseModel):
    artist: Artist
    streamable: str
    image: list[Image]
    mbid: str
    album: Album
    name: str
    nowplaying: typing.Optional[_Attr] = pydantic.Field(None, alias='@attr')
    url: str
    date: typing.Optional[Date] = None


class PageData(pydantic.BaseModel):
    perPage: str
    totalPages: str
    page: str
    user: str
    total: str


class RecentTracks(pydantic.BaseModel):
    tracks: list[Track] = pydantic.Field(..., alias='track')
    attr: PageData = pydantic.Field(..., alias='@attr')


class ScrobbleData(pydantic.BaseModel):
    recenttracks: RecentTracks
