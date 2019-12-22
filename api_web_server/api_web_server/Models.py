from datetime import datetime

from peewee import *

from settings import DataBase

db = PostgresqlDatabase(database=DataBase.base,
                        autocommit=True,
                        autorollback=True,
                        user=DataBase.username,
                        password=DataBase.password,
                        host=DataBase.host,
                        port=DataBase.port)


# sqlite_db = SqliteDatabase(':memory:', pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = db

    @classmethod
    def recreate_tables(cls):
        db.connect(reuse_if_open=True)
        table_list = db.get_tables()
        for model in cls.__subclasses__():
            if model.__name__.lower() not in table_list:
                print(model.__name__)
                db.create_tables([model])
                print(f'Table {model} was not found in DB. New table was created to fix that.')


class Test(BaseModel):
    place_id = PrimaryKeyField(index=True, unique=True)
    name = TextField()
    address = TextField()


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
        # data_set: List[Tuple[int, str, str]]
        """
        Insert list of tuples into Table
        :param data_set: list with tuples of (type foreign key, order foreign key, serial number value)
        :return: nothing
        """
        for chunk in range(0, len(data_set), 1000):
            rows = data_set[chunk:chunk + 1000]
            cls.insert_many(rows, fields=[cls.place_id, cls.name, cls.address]).execute()


class Events(BaseModel):
    id = PrimaryKeyField(index=True)
    date = TimestampField()
    title = TextField()
    place = ForeignKeyField(Places)
    slug = TextField(unique=True)
    price = TextField()
    hash_string = TextField()
    message_sent = BooleanField(default=False)

    @classmethod
    def add(cls, date: datetime, title: str, place: str, slug: str, hash_string: str, price: str,
            message_sent: bool) -> 'Events':
        try:
            return cls.get(
                (cls.date == date), (cls.title == title), (cls.place == place), (cls.slug == slug),
                (cls.price == price), (cls.hash_string == hash_string), (cls.message_sent == message_sent))
        except cls.DoesNotExist:
            new = cls.create(date=date, title=title, place=place, slug=slug, price=price, hash_string=hash_string,
                             message_sent=message_sent)
            return new
