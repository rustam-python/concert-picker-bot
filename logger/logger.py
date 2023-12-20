import logging
import sys

SUCCESS = 25
FAILURE = logging.CRITICAL


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = '\033[90m'
    yellow = '\033[93m'
    white = '\33[97m'
    red = '\033[91m'
    green = '\033[92m'
    bold_red = '\033[91m\033[1m'
    reset = '\033[0m'
    custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: white,
        SUCCESS: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def __init__(self):
        super().__init__(fmt=self.custom_format, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record) -> str:
        if record.exc_info is not None:
            return f'\n{self.red}{super(CustomFormatter, self).format(record)}{self.reset}\n'
        else:
            return f'{self.FORMATS.get(record.levelno)}{super(CustomFormatter, self).format(record)}{self.reset}'


class CustomLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name)
        self.setLevel(level=self.level)
        self._primary_handler = logging.StreamHandler(stream=sys.stdout)
        self._primary_handler.setLevel(level=level)
        self._primary_handler.setFormatter(CustomFormatter())
        self.addHandler(self._primary_handler)
        logging.addLevelName(SUCCESS, 'SUCCESS')
        logging.addLevelName(FAILURE, 'FAILURE')

    def progress_bar(self,
                     iteration: int,
                     total: int,
                     level: int = logging.DEBUG,
                     prefix: str = '',
                     suffix: str = '',
                     decimals: int = 1,
                     length: int = 80,
                     *args, **kwargs) -> None:
        """
        Call in a loop to create terminal progress bar.

        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            level       - Optional  : logging level (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
        """

        fill: str = '█'
        progress = 100 * (iteration / float(total))
        if progress > 100:
            progress = 100
        percent = ("{0:." + str(decimals) + "f}").format(progress)
        filled_length = int(length * iteration // total)
        if filled_length > length:
            filled_length = length
        bar = fill * filled_length + '-' * (length - filled_length)
        self._primary_handler.terminator = '\n' if iteration >= total else '\r'
        self._log(level, f'\r{prefix} |{bar}| {percent}% {suffix}', args, **kwargs)
        self._primary_handler.flush()
        self._primary_handler.terminator = '\n'

    def success(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'SUCCESS'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.success("Houston, we have a %s", "major success", exc_info=1)
        """
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    def failure(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'FAILURE'."""
        if self.isEnabledFor(FAILURE):
            self._log(FAILURE, msg, args, **kwargs)

    def direct(self, msg: str) -> None:
        """
        Directly wrights message into stdout without formatting and level validation.
        For passing out machine readable output.
        :param msg - message string
        """
        self._primary_handler.stream.write(f'{msg}{self._primary_handler.terminator}')
        self._primary_handler.flush()
