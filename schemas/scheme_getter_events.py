import datetime

import pydantic
import typing


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


class Events(pydantic.BaseModel):
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


class Artists(pydantic.BaseModel):
    topartists: _TopArtists
