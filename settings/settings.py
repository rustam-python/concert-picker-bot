import os

from configorm import IntegerField, StringField, Section, IniConnector


connector = IniConnector(connection_string=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cpb-config.ini'))


def check_config_integrity():
    BaseSection.check_config_integrity()


class BaseSection(Section):
    class Meta:
        connector = connector


class APIs(BaseSection):
    kudago_url = StringField(default='https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&fields=id,dates,title,place,slug,price&expand=&order_by=&text_format=&ids=&location=msk&actual_since={}&actual_until=&is_free=&categories=concert')  # noqa: E501
    url_top_artists = StringField(default='http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={user}&period=overall&limit={}&api_key={api_key}&format=json')  # noqa: E501
    url_recent_tracks = StringField(default='http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=200&user={user}&api_key={api_key}&format=json') # noqa: E501
    url_recent_tracks_via_page = StringField(default='http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=200&page={page}&user={user}&api_key={api_key}&format=json')  # noqa: E501
    lastfm_username = StringField(null=True)
    api_key = StringField(null=True)
    lastfm_artists_limit = IntegerField(default=300)
    telegram_token = StringField(null=True)
    telegram_chat_id = IntegerField(null=True)


class DataBase(BaseSection):
    username = StringField(null=True)
    password = StringField(null=True)
    host = StringField(null=True)
    port = StringField(null=True)
    name = StringField(null=True)
    transaction_retry_limit = IntegerField(default=5)
    bunch_size = IntegerField(default=1000)


class App(BaseSection):
    bot_request_timeout = IntegerField(default=3600)
    data_getter_timeout = IntegerField(default=18000)
    sentry_url = StringField(null=True)
    name = StringField(default='CPB and Scrobbler')


class Redis(BaseSection):
    host = StringField(null=True)
    port = IntegerField(null=True)
    password = StringField(null=True)
    db_cache = IntegerField(null=True)
    ttl = IntegerField(default=604800)
