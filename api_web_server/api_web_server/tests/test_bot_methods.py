import datetime
import json
import os
import unittest

import mock
import peewee
import requests
from freezegun import freeze_time

from bot_methods import BotMethods


class BotMethodsTest(unittest.TestCase):

    def setUp(self):
        self.events_list = [{'id': 2, 'title': 'предновогоднее мультимедийное шоу саундтреков «Кинозвук»',
                             'date': datetime.datetime(2019, 12, 21, 18, 0), 'price': 'от 1000 до 5000 рублей',
                             'slug': 'kontsert-kinozvuk-dekabr-2019', 'p_id': 745,
                             'name': 'Московский международный Дом музыки (ММДМ)',
                             'address': 'наб. Космодамианская, д. 52, стр. 8'}]
        with open(os.path.join(os.path.abspath('tests'), 'test_data', 'telegram_answer.txt'), 'r') as f:
            row_data = f.read()
            self.telegram_answer = eval(row_data)

        self.empty_events_list = []

        self.bot_methods_instance = BotMethods()

        patcher_telebot = mock.patch('bot_methods.TeleBot')
        self.addCleanup(patcher_telebot.stop)
        self.patched_telebot = patcher_telebot.start()

        patcher_events = mock.patch('bot_methods.Events')
        self.addCleanup(patcher_events.stop)
        self.patched_events = patcher_events.start()

        patcher_places = mock.patch('bot_methods.Places')
        self.addCleanup(patcher_places.stop)
        self.patcher_places = patcher_places.start()

        patcher_requests_get = mock.patch('bot_methods.requests.get')
        self.addCleanup(patcher_requests_get.stop)
        self.patched_requests_get = patcher_requests_get.start()

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_and_send_message_returns_list(self):
        self.assertIsInstance(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            list)

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_and_send_message_result_has_data(self):
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- Event "2" has been successfully sent.'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_and_send_message_result_no_data(self):
        self.assertEqual(self.bot_methods_instance.get_and_send_message(events=self.empty_events_list,
                                                                        bot_instance=self.patched_telebot),
                         [f'2019-12-17 14:03:19.655491 --- There are no new data.'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_return_Telebot_except(self):
        self.patched_telebot.send_message.side_effect = requests.exceptions.ConnectionError(
            'Failed to establish a new connection: [Errno 101] Network is unreachable')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- There is an error for "2" row: "Failed to '
             'establish a new connection: [Errno 101] Network is unreachable".'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_events_data_error_except(self):
        self.patched_events.update.side_effect = peewee.DataError(
            'No rows has been updated; may be an internal problem')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- There is an error for "2" row: "No rows has been updated; may be'
             ' an internal problem".'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_events_programming_except(self):
        self.patched_events.update.side_effect = peewee.ProgrammingError('relation "test" does not exist')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- There is an error for "2" row: "relation "test" does not exist".'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_events_key_error_except(self):
        self.patched_events.update.side_effect = KeyError('test_key')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- There is no "\'test_key\'" value in "2" row.'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_events_except(self):
        self.patched_events.update.side_effect = Exception('Exception occurred.')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- Exception occurred.'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_message_send_telebot_except(self):
        self.patched_telebot.send_message.side_effect = Exception('Exception occurred.')
        self.assertEqual(
            self.bot_methods_instance.get_and_send_message(events=self.events_list, bot_instance=self.patched_telebot),
            ['2019-12-17 14:03:19.655491 --- Exception occurred.'])

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_reference_from_api_requests_exception(self):
        self.patched_requests_get.side_effect = requests.exceptions.ConnectionError(
            "HTTPConnectionPool (host='0.0.0.0', port=5005): Max retries exceeded with url: /get_reference (Caused"
            " by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7efd5619c690>: Failed to"
            " establish a new connection: [Errno 111] Connection refused'))")
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            self.bot_methods_instance.get_reference_from_api()
            self.patched_requests_get.assert_called_once()

        # Test exception messages are equal.
        self.assertEqual("2019-12-17 14:03:19.655491 --- There is an error: \"HTTPConnectionPool (host='0.0.0.0', port="
                         "5005): Max retries exceeded with url: /get_reference (Caused by NewConnectionError('<urllib3."
                         "connection.HTTPConnection object at 0x7efd5619c690>: Failed to establish a new connection:"
                         " [Errno 111] Connection refused'))\".", str(context.exception))

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_reference_from_api_json_exception(self):
        self.patched_requests_get.return_value.json.side_effect = json.decoder.JSONDecodeError(
            'Expecting value', doc='line 1 column 1', pos=0)
        with self.assertRaises(requests.exceptions.ConnectionError) as context:
            self.bot_methods_instance.get_reference_from_api()
            self.patched_requests_get.assert_called_once()
        self.assertEqual("2019-12-17 14:03:19.655491 --- There is an error: \"Expecting value: line 1 column 1 "
                         "(char 0)\".", str(context.exception))

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_reference_from_api_result_is_json(self):
        self.patched_requests_get.return_value.json.return_value = {
            'id': 31910,
            'title': 'стадион «ВТБ Арена — Центральный стадион “Динамо”»',
            'slug': 'sportivnoe-sooruzhenie-vtb-arena---tsentralnyij-stadion-dinamo',
            'address': 'Ленинградский проспект, д. 36 стр. 1',
            'phone': '', 'subway': 'Динамо', 'location': 'msk',
            'site_url': 'https://kudago.com/msk/place/sportivnoe-sooruzhenie-vtb-arena---tsentralnyij-stadion-dinamo/',
            'is_closed': False,
            'coords': {'lat': 55.79119813172157,
                       'lon': 37.55982640731557},
            'is_stub': True}
        self.assertIsNotNone(self.bot_methods_instance.get_reference_from_api())
        self.assertIsInstance(self.bot_methods_instance.get_reference_from_api(), dict)

    @freeze_time("2019-12-17 14:03:19.655491")
    def test_get_reference_from_api_result_is_empty(self):
        self.patched_requests_get.return_value.json.return_value = None
        self.assertIsNone(self.bot_methods_instance.get_reference_from_api())


if __name__ == "__main__":
    unittest.main()
