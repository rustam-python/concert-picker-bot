from datetime import datetime
from logging import getLogger

from peewee import PostgresqlDatabase, Model, PrimaryKeyField, TextField, TimestampField, ForeignKeyField, \
    BooleanField, SqliteDatabase, Proxy, OperationalError, InterfaceError, CompositeKey, IntegerField

from .settings import DataBase

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
                    server_db.init(database=DataBase.base, user=DataBase.username, password=DataBase.password,
                                   host=DataBase.host, port=DataBase.port)
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
    place_id = PrimaryKeyField(index=True, unique=True)
    name = TextField()
    address = TextField()

    @classmethod
    def add(cls, place_id: int, name: str, address: str) -> 'Events':
        try:
            return cls.get(
                (cls.place_id == place_id), (cls.name == name), (cls.address == address))
        except cls.DoesNotExist:
            new = cls.create(place_id=place_id, name=name, address=address)
            return new

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


class Events(BaseModel):
    event_id = IntegerField()
    date = TimestampField()
    title = TextField()
    place = ForeignKeyField(Places)
    slug = TextField()
    price = TextField()
    message_sent = BooleanField(default=False)

    class Meta:
        primary_key = CompositeKey('event_id', 'date', 'title', 'place', 'slug', 'price', 'message_sent')

    @classmethod
    def add(cls, date: datetime, title: str, place: str, slug: str, hash_string: str, price: str,
            message_sent: bool) -> 'Events':
        try:
            return cls.get(
                (cls.date == date), (cls.title == title), (cls.place == place), (cls.slug == slug),
                (cls.price == price), (cls.message_sent == message_sent))
        except cls.DoesNotExist:
            new = cls.create(date=date, title=title, place=place, slug=slug, price=price, hash_string=hash_string,
                             message_sent=message_sent)
            return new
