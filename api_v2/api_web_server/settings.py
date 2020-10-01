import os

from configorm import IniConnector, Section, StringField, IntegerField

connector = IniConnector(connection_string=os.path.join(os.getcwd(), '../api-web-server-config.ini'))


class BaseSection(Section):
    class Meta:
        connector = connector


class DataBase(BaseSection):
    username = StringField(null=True)
    password = StringField(null=True)
    host = StringField(null=True)
    port = StringField(null=True)
    base = StringField(null=True)


class Server(BaseSection):
    host = StringField(null=True)
    port = IntegerField(null=True)
    username = StringField(null=True)
    last_fm_api_key = StringField(null=True)
    telegram_token = StringField(null=True)
