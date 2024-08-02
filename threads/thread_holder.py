import typing

import settings
import threads


class ThreadHolder:
    _thread_concerts_data: None | threads.ThreadConcertsDataGetter = None
    _thread_bot: None | threads.ThreadBot = None
    _thread_scrobbles_data: None | threads.ThreadScrobblesDataGetter = None


    @classmethod
    def start_threads(cls) -> None:
        """Stat all necessary threads."""
        for thread in (cls.get_concerts_data_thread(), cls.get_bot_thread(), cls.get_scrobble_data_thread()):
            thread.join()

    @classmethod
    def stop_threads(cls) -> None:
        for thread in cls._thread_scrobbles_data, cls._thread_bot, cls._thread_concerts_data:
            if thread:
                thread.stop()
                thread.join()

    @classmethod
    def get_concerts_data_thread(cls) -> threads.ThreadConcertsDataGetter:
        if cls._thread_concerts_data is None:
            cls._thread_concerts_data = threads.ThreadConcertsDataGetter(timeout=settings.App.data_getter_timeout)
            cls._thread_concerts_data.start()
        return cls._thread_concerts_data

    @classmethod
    def get_bot_thread(cls) -> threads.ThreadBot:
        if cls._thread_bot is None:
            cls._thread_bot = threads.ThreadBot(timeout=settings.App.bot_request_timeout)
            cls._thread_bot.start()
        return cls._thread_bot

    @classmethod
    def get_scrobble_data_thread(cls) -> threads.ThreadScrobblesDataGetter:
        if cls._thread_scrobbles_data is None:
            cls._thread_scrobbles_data = threads.ThreadScrobblesDataGetter(timeout=settings.App.bot_request_timeout)
            cls._thread_scrobbles_data.start()
        return cls._thread_scrobbles_data
