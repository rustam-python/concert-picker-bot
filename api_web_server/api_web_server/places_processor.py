from typing import List, Tuple, Dict, Set

import requests

from Models import Places


class Place:
    def __init__(self, place_id, place_title, place_address):
        self.place_id = place_id
        self.place_title = place_title
        self.place_address = place_address


class PlacesProcessor:
    def __init__(self, events_list: List[Dict[str, str]]):
        self.events_list: List[Dict[str, str]] = events_list
        self.places_id_set: Set[int] = set()
        self.places_attribs_list: List[Tuple[int, str, str]] = []
        self.places_cache: List[str] = []
        self.compared_places_attribs_list: List[Tuple[int, str, str]] = []

    def process(self):
        if self.get_places_id_set():
            if self.get_places_attribs():
                if self.db_compare():
                    Places.bunch_insert(self.compared_places_attribs_list)

    def get_places_id_set(self) -> Set[str]:
        places_list = [place['place']['id'] for place in self.events_list]
        self.places_id_set = set(places_list)

        return self.places_id_set

    def get_places_attribs(self) -> List[Tuple[int, str, str]]:
        for place_id in self.places_id_set:
            result = requests.get(
                f'https://kudago.com/public-api/v1.4/places/{place_id}/?lang=&fields=id,title,address&location=msk')
            results = result.json()
            """Check if ID is not in cache"""
            if results['id'] not in self.places_cache:
                self.places_attribs_list.append((results['id'], results['title'], results['address']))
                self.places_cache.append(results['id'])
        return self.places_attribs_list

    def db_compare(self):
        places_from_db: List[int] = [place['place_id'] for place in Places.select().dicts().execute()]
        # find the difference between ids from Db and ids from returned requests.
        diff: List[int] = [place for place in self.places_id_set if place not in places_from_db]
        if diff:
            # get all attribs for places in difference.
            self.compared_places_attribs_list = [place for place in self.places_attribs_list if place[0] in diff]
            return self.compared_places_attribs_list
