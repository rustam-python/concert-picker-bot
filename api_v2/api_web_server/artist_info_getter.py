from typing import List

import musicbrainzngs
import requests

from api_v2.api_web_server.error import LastFMResponseError
from api_v2.api_web_server.logging_utils import get_logger
from api_v2.api_web_server.main import EventsGetter
from api_v2.api_web_server.settings import Server

musicbrainzngs.set_useragent(
    "artist-info-getter",
    "0.1"
)
logger = get_logger('Artist Getter')


def _recursive_artist_getter(username:str, token: str, page: int = 1):
    response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&'
                            f'period=overall&limit={1000}&page={page}&api_key={token}&format=json')
    _json = response.json()
    if _json.get('error'):
        message = f'LastFM API is returned an error - {_json.get("message")}'
        logger.critical(message)
        raise LastFMResponseError(message)
    data: List[str] = []

    # Get all artist names on page.
    for artist in _json['topartists']['artist']:
        data.append(artist['name'])

    # If there are no more pages left
    if _json['topartists']['@attr']['page'] == _json['topartists']['@attr']['totalPages']:
        return data
    else:
        page += 1
        return data + _recursive_artist_getter(username, token, page)
