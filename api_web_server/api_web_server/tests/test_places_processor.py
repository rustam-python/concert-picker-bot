import datetime
import json
import os
import unittest

import mock
import peewee
import requests
from freezegun import freeze_time

from places_processor import PlacesProcessor


class PlacesProcessorTest(unittest.TestCase):

    def setUp(self):
        self.events_list = [
            {'id': 182452, 'dates': [{'start': 1590336000, 'end': 1590336000}], 'title': 'концерт Green Day',
             'slug': 'kontsert-green-day', 'place': {'id': 17714}, 'price': 'от 3000 до 14000 рублей',
             'hash_string': '759fbc75b91e87143c94cfa516333eec'},
            {'id': 184482, 'dates': [{'start': 1577984400, 'end': 1577984400}], 'title': 'концерт Noize MC',
             'slug': 'kontsert-noize-mc-2020', 'place': {'id': 418}, 'price': 'от 2000 до 6000 рублей',
             'hash_string': '56c585df108e2375d3a60efaf2f497e2'},
            {'id': 183849, 'dates': [{'start': 1593705600, 'end': 1593705600}], 'title': 'концерт Iron Maiden',
             'slug': 'kontsert-iron-maiden', 'place': {'id': 31910}, 'price': 'уточняется',
             'hash_string': '6933fe5122cc9c5d244db478f6c995e5'},
            {'id': 183890, 'dates': [{'start': 1593536400, 'end': 1593536400}], 'title': 'концерт Korn',
             'slug': 'kontsert-korn-iyun-2020', 'place': {'id': 31910}, 'price': 'от 3500 до 8500 рублей',
             'hash_string': 'caed2840f81721918c2d73a62ab45ee0'},
            {'id': 184144, 'dates': [{'start': 1577804400, 'end': 1577804400}], 'title': 'концерт группы «Сплин»',
             'slug': 'kontsert-splin-dekabr-2019', 'place': {'id': 526}, 'price': 'от 3000 до 20000 рублей',
             'hash_string': '841d50ed0f4c1825b8d2905163dee8fc'}
        ]

        self.places_processor_instance = PlacesProcessor(events_list=self.events_list)

        patcher_requests_response = mock.patch('events_processor.requests.models.Response')
        self.addCleanup(patcher_requests_response.stop)
        self.patched_requests_response = patcher_requests_response.start()

        patcher_requests_get = mock.patch('events_processor.requests.get')
        self.addCleanup(patcher_requests_get.stop)
        self.patched_requests_get = patcher_requests_get.start()

        server = mock.patch('events_processor.Server')
        self.addCleanup(server.stop)
        self.server = server.start()

        self.server.host = '0.0.0.0'
        self.server.port = '5005'
        self.server.user = 'user'
        self.server.last_fm_api_key = 'fake_key'


class GetPlacesIDSetTest(PlacesProcessorTest):
    def test_get_places_id_set_return(self):
        places_id_set = set([place['place']['id'] for place in self.events_list])
        self.assertEqual(self.places_processor_instance.get_places_id_set(), places_id_set)

    def test_get_places_id_set_return_set(self):
        self.assertIsInstance(self.places_processor_instance.get_places_id_set(), set)

    def test_get_places_id_set_if_get_empty_events_list(self):
        self.places_processor_instance.events_list = []
        with self.assertRaises(ValueError) as context:
            self.places_processor_instance.get_places_id_set()
        # Test exception messages are equal.
        self.assertEqual("Events list is empty!", str(context.exception))


class GetPlacesAttribsTest(PlacesProcessorTest):
    def test_get_places_attribs_return(self):
        places_id_set = set([place['place']['id'] for place in self.events_list])
        self.assertEqual(self.places_processor_instance.get_places_id_set(), places_id_set)


if __name__ == "__main__":
    unittest.main()
