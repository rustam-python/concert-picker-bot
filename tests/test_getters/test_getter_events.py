import unittest
from unittest.mock import patch, Mock

from getters import ConcertsGetter


class TestLastFMScrobbleDataGetter(unittest.TestCase):
    """
    Base class for "LastFMScrobbleDataGetter" tests
    """

    def setUp(self) -> None:
        """Set up test."""
        with patch('getters.getter_lastfm_scrobble_data.logger'):
            self.getter = ConcertsGetter()


class TestGetData(TestLastFMScrobbleDataGetter):
    def test_get_data_get_kudago_data_failure(self):
        self.getter._get_kudago_data = Mock()