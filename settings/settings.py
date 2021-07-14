import os

from configorm import IntegerField, StringField, Section, IniConnector

connection_string = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cpb-config.ini')

connector = IniConnector(connection_string=connection_string)


def check_config_integrity():
    BaseSection.check_config_integrity()


class BaseSection(Section):
    class Meta:
        connector = connector


class APIs(BaseSection):
    kudago_url = StringField(
        default='https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&fields=id,dates,title,place,slug,price&'
                'expand=&order_by=&text_format=&ids=&location=msk&actual_since={}&actual_until=&is_free=&'
                'categories=concert')
    lastfm_url = StringField(
        default='http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&period=overall&limit={}&'
                'api_key={}&format=json')
    lastfm_username = StringField(null=True)
    lastfm_token = StringField(null=True)
    lastfm_artists_limit = IntegerField(default=300)
    telegram_token = StringField(null=True)
    telegram_chat_id = IntegerField(null=True)


class DataBase(BaseSection):
    username = StringField(null=True)
    password = StringField(null=True)
    host = StringField(null=True)
    name = StringField(null=True)
    transaction_retry_limit = IntegerField(default=5)
    bunch_size = IntegerField(default=1000)


class App(BaseSection):
    delay_time = IntegerField(default=3600)
