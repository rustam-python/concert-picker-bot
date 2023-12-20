import datetime
import functools
import importlib
import inspect
import os
import typing

from peewee import (
    CharField, Model, ForeignKeyField, IntegerField, Proxy, SqliteDatabase, BooleanField, DateTimeField, AutoField,
    PostgresqlDatabase
)

import cache
import settings

local_db = SqliteDatabase(os.path.join(os.path.dirname(__file__), 'cpb-local-db'))
server_db = PostgresqlDatabase(database='', autorollback=True)
db = Proxy()


def initialize_data_base(is_local: bool = True) -> Proxy:
    if not is_local:
        server_db.init(
            database=settings.DataBase.name,
            user=settings.DataBase.username,
            host=settings.DataBase.host,
            port=settings.DataBase.port,
            password=settings.DataBase.password
        )
        server_db.connect(reuse_if_open=True)
        db.initialize(server_db)
        print('Database initialised as remote')
    else:
        db.initialize(local_db)
        print('Database initialised as local')
    BaseModel.recreate_tables()
    return db


class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def recreate_tables(cls):
        db.connect(reuse_if_open=True)
        table_list = db.get_tables()
        highest_priority = cls._find_highest_migration_priority()
        for priority in (range(highest_priority + 1)):
            for model in cls._get_models():
                if model.migration_priority == priority:
                    if model.__name__.lower() not in table_list and 'mixin' not in model.__name__.lower():
                        db.create_tables([model])
                        print(f'Table {model.__name__} was not found in DB. New table was created to fix that.')

    @staticmethod
    @functools.lru_cache
    def _get_models():
        return [
            member[1] for member in inspect.getmembers(
                importlib.import_module('database.models'),
                lambda m: inspect.isclass(m) and Model in m.__mro__ and not m.__subclasses__())
        ]

    @classmethod
    def _find_highest_migration_priority(cls):
        highest_priority = 0
        for model in cls._get_models():
            if model.migration_priority > highest_priority:
                highest_priority = model.migration_priority
        return highest_priority


class Places(BaseModel):
    migration_priority = 0

    place_id = IntegerField(primary_key=True, index_type=True)
    address = CharField()
    title = CharField()

    @classmethod
    def add(cls, place_id: int, address: str, title: str) -> 'Places':
        try:
            return cls.get(cls.place_id == place_id)
        except cls.DoesNotExist:
            new = cls.create(
                place_id=place_id,
                address=address,
                title=title
            )
            return new


class Events(BaseModel):
    migration_priority = 1

    event_id = IntegerField(primary_key=True)
    title = CharField()
    slug = CharField()
    place_id = ForeignKeyField(Places, null=True)
    price = CharField(null=True)
    is_sent = BooleanField(default=False)
    updated = BooleanField(default=False)

    @classmethod
    def add(cls,
            event_id: int,
            title: str,
            slug: str,
            place_id: typing.Optional[int],
            price: typing.Optional[str]
            ) -> 'Events':
        try:
            return cls.get(cls.event_id == event_id)
        except cls.DoesNotExist:
            new = cls.create(
                event_id=event_id,
                title=title,
                slug=slug,
                place_id=Places.get(place_id=place_id),
                price=price
            )
            return new

    @classmethod
    def mark_as_sent(cls):
        cls.update(is_sent=True).where(Events.event_id == cls.event_id).execute()

    @classmethod
    def mark_as_unsent(cls):
        cls.update(is_sent=False).where(Events.event_id == cls.event_id).execute()


class EventDates(BaseModel):
    migration_priority = 2

    event_id = ForeignKeyField(Events)
    date_start = DateTimeField()
    date_stop = DateTimeField()

    @classmethod
    def add(cls, event_id: int, date_start: datetime.datetime, date_stop: datetime.datetime) -> 'EventDates':
        return cls.get_or_create(event_id=event_id, date_start=date_start, date_stop=date_stop)[0]


D = typing.TypeVar('D', bound='_DictionaryModel')


class _DictionaryModel(BaseModel):
    """Base class for models that describe Database dictionary tables."""

    migration_priority = 0

    id = AutoField()
    name = CharField(unique=True)

    @classmethod
    def add(cls: typing.Type[D], name: str) -> 'D':
        return cls.get_or_create(name=name)[0]


class Artists(_DictionaryModel):
    pass


class Albums(_DictionaryModel):
    pass


class Tracks(_DictionaryModel):
    pass


class LogLevel(_DictionaryModel):
    pass


class Scrobbles(BaseModel):
    migration_priority = 1

    id = AutoField()
    artist = ForeignKeyField(Artists)
    album = ForeignKeyField(Albums)
    track = ForeignKeyField(Tracks)
    scrobble_date = DateTimeField(unique=True)

    @classmethod
    def add(cls, artist: str, album: str, track: str, scrobble_date: datetime.datetime) -> 'Scrobbles':
        try:
            return cls.get(cls.scrobble_date == scrobble_date)
        except cls.DoesNotExist:
            return cls.create(
                track=cache.Caching.get_track_id(track),
                artist=cache.Caching.get_artist_id(artist),
                album=cache.Caching.get_album_id(album),
                scrobble_date=scrobble_date
            )


class Log(BaseModel):
    migration_priority = 1

    id = AutoField()
    date = DateTimeField()
    message = CharField()
    level = ForeignKeyField(LogLevel)

    @classmethod
    def add(cls, date: datetime.datetime, message: str, level: str) -> 'Log':
        return cls.create(
            date=date,
            message=message,
            level=LogLevel.add(level)
        )
