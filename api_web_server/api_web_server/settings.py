from configorm import *

connector = IniConnector(connection_string='api-web-server-config.ini')


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
    user = StringField(null=True)
    last_fm_api_key = StringField(null=True)
    telegram_token = StringField(null=True)
