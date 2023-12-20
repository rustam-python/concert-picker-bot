"""
Unit tests for "getters.getter_lastfm_scrobble_data.LastFMScrobbleDataGetter" class
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from getters import LastFMScrobbleDataGetter


class TestLastFMScrobbleDataGetter(unittest.TestCase):
    """
    Base class for "LastFMScrobbleDataGetter" tests
    """

    def setUp(self) -> None:
        """Set up test."""
        with patch('getters.getter_lastfm_scrobble_data.logger'), \
             patch('getters.getter_lastfm_scrobble_data.asyncio') as async_mock:
            self.async_mock = async_mock
            self.getter = LastFMScrobbleDataGetter()


class TestInit(TestLastFMScrobbleDataGetter):
    """
    Unit tests for "_ProtoWorkerBMCUpdater.__init__" method
    """

    def test_instance_attrs(self):
        """
        Tests values of "_ProtoWorkerBMCUpdater"
        instance attributes
        """
        # Assertions

        self.assertEqual(self.getter._pages_for_retry, [])


@patch('getters.getter_lastfm_scrobble_data.time')
@patch('getters.getter_lastfm_scrobble_data.cache')
class TestGetScrobbles(TestLastFMScrobbleDataGetter):
    """
    Unit tests for "_ProtoWorkerBMCUpdater.get_scrobbles" method
    """

    def test_get_scrobbles_is_ok(self, cache_mock: MagicMock, time_mock: MagicMock):

        # Setup

        scrobble = Mock(track=Mock(), artist=Mock(), album=Mock(), scrobble=Mock())
        page = Mock(scrobbles=[scrobble])
        self.getter._get_pages = Mock(return_value=[page])

        # Run

        self.getter.get_scrobbles()

        # Assertions

        cache_mock.Caching.get_scrobble_id.assert_called_once_with(
            track=scrobble.track,
            artist=scrobble.artist,
            album=scrobble.album,
            scrobble_date=scrobble.date
        )

    @patch('getters.getter_lastfm_scrobble_data.sentry')
    def test_get_scrobbles_exception(self, sentry_mock: MagicMock, cache_mock: MagicMock, time_mock: MagicMock):
        # Setup

        exception = Exception()
        self.getter._get_pages = Mock(side_effect=exception)

        # Run

        self.getter.get_scrobbles()

        # Assertions

        cache_mock.Caching.get_scrobble_id.assert_not_called()
        sentry_mock.capture_exception.assert_called_once_with(exception)


class TestGetPages(TestLastFMScrobbleDataGetter):
    """
    Unit tests for "_ProtoWorkerBMCUpdater.get_scrobbles" method.
    """

    def test__get_pages_is_ok(self,):

        # Setup

        self.getter._get_total_pages_count = Mock()
        self.getter._make_requests = Mock()

        # Run

        self.getter.get_scrobbles()

        # Assertions
