import typing

import settings
from threads import BotThread


class ThreadHolder:
    _bot_thread: typing.Optional[BotThread] = None

    @classmethod
    def stop_threads(cls) -> None:
        for thread in (cls._bot_thread,):
            if thread:
                thread.stop()
                thread.join()

    @classmethod
    def get_bot_thread(cls) -> BotThread:
        if cls._bot_thread is None:
            cls._bot_thread = BotThread(settings.App.bot_request_timeout)
            cls._bot_thread.start()
        return cls._bot_thread
