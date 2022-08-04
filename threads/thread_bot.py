import datetime
import threading
import time

import bot
import logger


class BotThread(threading.Thread):
    def __init__(self, timeout: int):
        self.logger = logger.Logger(name=self.__class__.__name__)
        self.timeout = timeout

        self._is_running = threading.Event()
        self._stop_event = threading.Event()

        self._is_running.set()

        super(BotThread, self).__init__()

        self.daemon = False
        self.name = self.__class__.__name__

    def run(self) -> None:
        while not self._stop_event.is_set():
            start_time = datetime.datetime.now()
            if self._is_running.is_set():
                while (datetime.datetime.now() - start_time).seconds < (self.timeout + 1):
                    time.sleep(2)
                try:
                    bot.Bot().start()
                except RuntimeError as e:
                    self.logger.warning(e, exc_info=True)

    def pause(self) -> None:
        self._is_running.clear()

    def stop(self) -> None:
        self._stop_event.set()
