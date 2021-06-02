from datetime import datetime
from logging import getLogger

from peewee import PostgresqlDatabase, Model, PrimaryKeyField, TextField, TimestampField, ForeignKeyField, \
    BooleanField, SqliteDatabase, Proxy, OperationalError, InterfaceError, CompositeKey, IntegerField

from api_v2.api_web_server import settings

logger = getLogger('Events parser')

server_db = PostgresqlDatabase(database='', autocommit=True, autorollback=True)
local_db = SqliteDatabase('sqlite.db')

"""Used for switching between different databases(sqlite, PostgreSQL)"""
db = Proxy()


def initialize_data_base(force_local: bool = False) -> Proxy:
    try:
        if force_local is False:
            if db.obj is None:
                try:
                    server_db.init(database=settings.DataBase.base,
                                   user=settings.DataBase.username,
                                   password=settings.DataBase.password,
                                   host=settings.DataBase.host,
                                   port=settings.DataBase.port)
                    server_db.connect(reuse_if_open=True)
                    db.initialize(server_db)
                    BaseModel.check_db_integrity()
                    logger.info('Database is initialized as remote!')
                    return db
                except (OperationalError, InterfaceError) as err:
                    logger.critical(str(err))
                    raise err
            else:
                if type(db.obj) is PostgresqlDatabase:
                    connection = db.obj.connection()
                    logger.info('Database already connected: %s' % connection)
        else:
            db.initialize(local_db)
            logger.info('Database is initialized as local!')
            return db
    except Exception as err:
        logger.critical(str(err))
        raise err


# sqlite_db = SqliteDatabase(':memory:', pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = db

    @classmethod
    def check_db_integrity(cls):
        db.connect(reuse_if_open=True)
        table_list = db.get_tables()
        for model in cls.__subclasses__():
            if model.__name__.lower() not in table_list:
                print(model.__name__)
                db.create_tables([model])
                print(f'Table {model} was not found in DB. New table was created to fix that.')


class Places(BaseModel):
    place_id = IntegerField(unique=True)
    name = TextField(null=True)
    address = TextField(null=True)

    @classmethod
    def add(cls, place_id: int, name: str = None, address: str = None) -> 'Places':
        try:
            return cls.get((cls.place_id == place_id), (cls.name == name), (cls.address == address))
        except cls.DoesNotExist:
            return cls.create(place_id=place_id, name=name, address=address)

    @classmethod
    def bunch_insert(cls, data_set):
        """
        Insert list of tuples into table.
        :param data_set: list with tuples of (type foreign key, order foreign key, serial number value)
        :return: nothing
        """
        for chunk in range(0, len(data_set), 1000):
            rows = data_set[chunk:chunk + 1000]
            cls.insert_many(rows, fields=[cls.place_id, cls.name, cls.address]).execute()


class Dates(BaseModel):
    id = PrimaryKeyField(index=True, unique=True)
    start = TimestampField(null=False)
    end = TimestampField(null=False)

    @classmethod
    def add(cls, start: datetime, end: datetime) -> 'Dates':
        return cls.get_or_create(start=start, end=end)[0]


class Events(BaseModel):
    event_id = IntegerField(index=True, unique=True)
    title = TextField(null=False)
    place = ForeignKeyField(Places, null=True)
    slug = TextField(null=False)
    price = TextField(null=False)
    message_sent = BooleanField(default=False)

    @classmethod
    def add(cls, event_id: int, title: str, place: int, slug: str, price: str) -> 'Events':
        try:
            return cls.get(event_id=event_id)
        except cls.DoesNotExist:
            new = cls.create(
                event_id=event_id,
                title=title,
                place=Places.add(place),
                slug=slug,
                price=price
            )
            return new


class EventsInDates(BaseModel):
    id = PrimaryKeyField(index=True, unique=True)
    event_id = ForeignKeyField(Events)
    dates_id = ForeignKeyField(Dates)

    @classmethod
    def add(cls, event_id: int, dates_id: int) -> 'EventsInDates':
        return cls.get_or_create(event_id=event_id, dates_id=dates_id)[0]
