import datetime
import json
import os
import unittest

import mock
import peewee
import requests
from freezegun import freeze_time

from events_processor import EventsProcessor


class EventsProcessorTest(unittest.TestCase):

    def setUp(self):
        self.events_processor_instance = EventsProcessor()

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

    def test_get_artists_list_settings(self):
        self.patched_requests_get.return_value = requests.models.Response
        self.patched_requests_get.url = f'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=' \
                                        f'{self.server.user}&period=overall&limit=300&api_key=' \
                                        f'{self.server.last_fm_api_key}&format=json'
        self.assertEqual(self.patched_requests_get.url,  f'http://ws.audioscrobbler.com/2.0/?method='
                                                         f'user.gettopartists&user=user&period=overall&limit=300&'
                                                         f'api_key=fake_key&format=json')

    def test_get_artists_list_requests_error(self):
        self.patched_requests_get.side_effect = requests.exceptions.ConnectionError(
            f"HTTPConnectionPool (host='{self.server.host}', port={self.server.port}): Max retries exceeded with url:"
            f" /get_reference (Caused by NewConnectionError("
            f"'<urllib3.connection.HTTPConnection object at 0x7efd5619c690>: Failed to establish a new connection:"
            f" [Errno 111] Connection refused'))")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            self.events_processor_instance.get_artists_list()

        # Test exception messages are equal.
        self.assertEqual(f"HTTPConnectionPool (host='{self.server.host}', port={self.server.port}): Max retries"
                         f" exceeded with url: /get_reference (Caused by NewConnectionError("
                         f"'<urllib3.connection.HTTPConnection object at 0x7efd5619c690>: Failed to establish a new"
                         f" connection: [Errno 111] Connection refused'))", str(context.exception))

    def test_get_artists_list_response_error(self):
        self.patched_requests_get.return_value = requests.models.Response
        self.patched_requests_response.json.return_value = {"error": 10, "message": "Invalid API key - You must "
                                                                                    "be granted a valid key by last.fm"}
        self.patched_requests_response.text = '{"error":10,"message":"Invalid API key - You must be granted a valid' \
                                              ' key by last.fm"}'
        with self.assertRaises(RuntimeError) as context:
            self.events_processor_instance.get_artists_list()

        # Test exception messages are equal.
        self.assertEqual('{"error":10,"message":"Invalid API key - You must be granted a valid key by last.fm"}',
                         str(context.exception))

    def test_get_artists_list_response(self):
        self.patched_requests_get.return_value = requests.models.Response
        with open(os.path.join(os.path.abspath('tests'), 'test_data', 'last_fm_answer.json')) as f:
            self.patched_requests_response.json.return_value = json.load(f)
        artists_list = [artist['name'] for artist in self.patched_requests_response.json()['topartists']['artist']]
        self.assertEqual(self.events_processor_instance.get_artists_list(), artists_list)

    def test_db_compare(self):
        pass


if __name__ == "__main__":
    unittest.main()
