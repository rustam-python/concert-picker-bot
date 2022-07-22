import threading
import typing

import settings
import threads


class ThreadHolder:
    _lastfm_data_thread: typing.Optional[threads.LastFMScrobbleDataThread] = None
    _bot_thread: typing.Optional[threads.BotThread] = None

    @classmethod
    def start_threads(cls) -> None:
        """Stat all necessary threads."""
        for thread in (cls.get_lastfm_data_thread(), cls.get_bot_thread()):
            thread.join()

    @classmethod
    def stop_threads(cls) -> None:
        for thread in cls._lastfm_data_thread, cls._bot_thread:
            if thread:
                thread.stop()
                thread.join()

    @classmethod
    def get_lastfm_data_thread(cls) -> threads.LastFMScrobbleDataThread:
        if cls._lastfm_data_thread is None:
            cls._lastfm_data_thread = threads.LastFMScrobbleDataThread(timeout=settings.App.data_getter_timeout)
            cls._lastfm_data_thread.start()
            [print(thread.name) for thread in threading.enumerate()]
            print(threading.active_count())
        return cls._lastfm_data_thread

    @classmethod
    def get_bot_thread(cls) -> threads.BotThread:
        if cls._bot_thread is None:
            cls._bot_thread = threads.BotThread(timeout=settings.App.bot_request_timeout)
            cls._bot_thread.start()
            [print(thread.name) for thread in threading.enumerate()]
            print(threading.active_count())
        return cls._bot_thread
