import datetime
import os
import typing

from peewee import CharField, Model, ForeignKeyField, IntegerField, Proxy, SqliteDatabase, \
    BooleanField, DateTimeField

local_db = SqliteDatabase(os.path.join(os.path.dirname(__file__), 'cpb-local-db'))
db = Proxy()


def initialize_data_base():
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

        for model in cls.__subclasses__():
            if model.__name__.lower() not in table_list and 'mixin' not in model.__name__.lower():
                db.create_tables([model])
                print(f'Table {model.__name__} was not found in DB. New table was created to fix that.')


class Place(BaseModel):
    place_id = IntegerField(primary_key=True, index_type=True)
    address = CharField()
    title = CharField()

    @classmethod
    def add(cls, place_id: int, address: str, title: str) -> 'EventDates':
        return cls.get_or_create(place_id=place_id, address=address, title=title)[0]


class Events(BaseModel):
    event_id = IntegerField(primary_key=True, index_type=True)
    title = CharField()
    slug = CharField()
    place_id = ForeignKeyField(Place, null=True)
    price = CharField(null=True)
    is_sent = BooleanField(default=False)

    @classmethod
    def add(cls,
            event_id: int,
            title: str,
            slug: str,
            place_id: typing.Optional[int],
            price: typing.Optional[str]) -> 'Events':
        return cls.get_or_create(event_id=event_id,
                                 title=title,
                                 slug=slug,
                                 place_id=Place.get(place_id=place_id),
                                 price=price)[0]

    def mark_as_sent(self):
        Events.update(is_sent=True).where(Events.event_id == self.event_id).execute()


class EventDates(BaseModel):
    event_id = ForeignKeyField(Events)
    date_start = DateTimeField()
    date_stop = DateTimeField()

    @classmethod
    def add(cls, event_id: int, date_start: datetime.datetime, date_stop: datetime.datetime) -> 'EventDates':
        return cls.get_or_create(event_id=event_id, date_start=date_start, date_stop=date_stop)[0]
