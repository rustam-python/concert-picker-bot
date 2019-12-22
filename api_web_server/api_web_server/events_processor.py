import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Union

import requests

from Models import Events
from places_processor import PlacesProcessor
from settings import Server


class EventsProcessor:

    def __init__(self):
        self.events_cache: List[str] = []
        self.events_list: List[Dict[str, str]] = []
        self.compared_events_list: List[Dict[str, str]] = []
        self.r_string = f'https://kudago.com/public-api/v1.4/events/?lang=&page=1&page_size=100&' \
                        f'fields=id,dates,title,place,slug,price&expand=&order_by=&text_format=&ids=&location=msk&' \
                        f'actual_since={time.time()}&actual_until=&is_free=&categories=concert'

    def process(self) -> Union[None, List[str]]:
        try:
            if Server.last_fm_api_key is None:
                raise RuntimeError('"lastFM_api_key" is non found! Please check if "api-web-server-config.ini" is in'
                                   ' code directory and correctly filled.')
            if Server.user is None:
                raise RuntimeError('"LastFM user" is non found! Please check if "api-web-server-config.ini" is in'
                                   ' code directory and correctly filled.')
            artists_list = self.get_artists_list()
            events_list = self.create_events_list(request_string=self.r_string, artists_list=artists_list)
            places = PlacesProcessor(events_list=events_list)
            places.process()
            if self.events_list:
                self.db_compare()
                if not self.compared_events_list:
                    return None
                else:
                    self.update_db()
                    return [event['slug'] for event in self.compared_events_list]

        except requests.exceptions.ConnectionError as err:
            print(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')
            raise requests.exceptions.ConnectionError(f'{datetime.now()} --- There is error: "{str(err).strip()}".')
        except json.decoder.JSONDecodeError as err:
            print(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')
            raise requests.exceptions.ConnectionError(f'{datetime.now()} --- There is error: "{str(err).strip()}".')
        except KeyError as err:
            print(f'{datetime.now()} --- There is an error: "{err}"')
            raise KeyError(f'{datetime.now()} --- There is an error: "{err}"')
        except RuntimeError as err:
            print(f'{datetime.now()} --- There is an error: "{err}"')
            raise RuntimeError(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')

    @classmethod
    def get_artists_list(cls) -> List[str]:
        result = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={Server.user}&'
                              f'period=overall&limit=300&api_key={Server.last_fm_api_key}&format=json')
        result_json = result.json()
        if "error" in result_json.keys():
            raise RuntimeError(result.text)
        artists_list = [artist['name'] for artist in result_json['topartists']['artist']]
        return artists_list

    def create_events_list(self, request_string: str, artists_list: List[str]) -> List[Dict[str, str]]:
        result = requests.get(request_string)
        results = result.json()['results']  # Get results from JSON.
        next_page = result.json()['next']  # Get next page from JSON.
        if next_page is None:
            pass
        else:
            for event in results:
                for artist in artists_list:
                    """If artist name is in event title - add event."""
                    if artist in event['title'] and event not in self.events_list:
                        # """Check if ID is not in cache"""
                        if event['id'] not in self.events_cache:  # add cash to cut off elements already there.
                            # get hash from place_id, date and price and add to event.
                            event['hash_string'] = hashlib.md5((str(event['place']['id']) + str(event['price']) + str(
                                event['dates'][0]['start'])).encode('utf-8')).hexdigest()
                            self.events_list.append(event)
                            self.events_cache.append(event['id'])
            self.create_events_list(request_string=next_page, artists_list=artists_list)
        return self.events_list

    def db_compare(self):
        # Get events hash list from DB.
        hash_list_from_db: List[str] = [event['hash_string'] for event in Events.select().dicts().execute()]
        # Get events hash list from returned API answer.
        hash_list: List[str] = [event['hash_string'] for event in self.events_list]
        # Find new events.
        diff: List[str] = [_hash for _hash in hash_list if _hash not in hash_list_from_db]
        if diff:
            self.compared_events_list = [event for event in self.events_list if event['hash_string'] in diff]
            return self.compared_events_list

    def update_db(self):
        for event in self.compared_events_list:
            Events.add(date=event['dates'][0]['start'],
                       title=event['title'],
                       place=event['place']['id'],
                       slug=event['slug'],
                       price=event['price'],
                       hash_string=event['hash_string'],
                       message_sent=False)


if __name__ == '__main__':
    events = EventsProcessor()
    events.get_artists_list()
