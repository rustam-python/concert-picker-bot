from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, conlist


class Place(BaseModel):
    id: int


class Dates(BaseModel):
    start: datetime
    end: datetime


class Event(BaseModel):
    id: int
    dates: List[Dates]
    title: str
    slug: str
    place: Optional[Place]
    price: str


class KudaGoEvents(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Event]


class KudaGoPlace(BaseModel):
    address: str
    id: int
    title: str


class TopArtistsAttr(BaseModel):
    page: str
    perPage: str
    total: str
    totalPages: str
    user: str


class ArtistsAttr(BaseModel):
    rank: str


class Image(BaseModel):
    _text: str
    size: str

    class Config:
        fields = {
            '_text': '#text'
        }


class Artist(BaseModel):
    _attr: ArtistsAttr
    image: conlist(Image, min_items=5, max_items=5)
    mbid: str
    name: str
    playcount: str
    streamable: str
    url: str

    class Config:
        fields = {
            '_attr': '@attr'
        }


class TopArtists(BaseModel):
    _attr: TopArtistsAttr
    artist: List[Artist]

    class Config:
        fields = {
            '_attr': '@attr'
        }


class LastFMResponse(BaseModel):
    topartists: TopArtists
