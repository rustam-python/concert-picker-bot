import typing

import settings
import threads


class ThreadHolder:
    _lastfm_data_thread: typing.Optional[threads.LastFMScrobbleDataThread] = None
    _bot_thread: typing.Optional[threads.BotThread] = None

    @classmethod
    def stop_threads(cls) -> None:
        for thread in cls._lastfm_data_thread, cls._bot_thread:
            if thread:
                thread.stop()
                thread.join()

    @classmethod
    def get_lastfm_data_thread(cls) -> threads.LastFMScrobbleDataThread:
        if cls._lastfm_data_thread is None:
            cls._lastfm_data_thread = threads.LastFMScrobbleDataThread(settings.App.data_getter_timeout)
            cls._lastfm_data_thread.start()
        return cls._lastfm_data_thread

    @classmethod
    def get_bot_thread(cls) -> threads.BotThread:
        if cls._bot_thread is None:
            cls._bot_thread = threads.BotThread(settings.App.bot_request_timeout)
            cls._bot_thread.start()
        return cls._bot_thread
