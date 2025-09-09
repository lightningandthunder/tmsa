import logging
import sys

from src import ERROR_FILE


class Tracer:
    def __init__(self, log_level: int, use_console: bool, use_file: bool):
        self.log_level = log_level
        self.use_file = use_file
        self.use_console = use_console

        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

        # Clear default handlers
        self.logger.handlers.clear()

        if use_console:
            # Console logging with colors
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)

            formatter = ColoredFormatter()
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)

    # TODO - We should store logs and then write them all at the end;
    # right now this just logs everything backwards
    def __log_to_file(self, log: str):
        if self.use_file:
            with open(ERROR_FILE, 'r') as file:
                contents = file.read()
                if len(contents) > 30000:
                    contents = contents[:30000]
            with open(ERROR_FILE, 'w') as file:
                file.write(log + '\n' + contents)

    def __format_log(self, name, val=None):
        if val is not None:
            return f'{name}: {val!r}'
        return str(name)

    def routine(self, name, val=None):
        if self.log_level <= logging.WARNING:
            log = self.__format_log(name, val)
            self.logger.warning(log)
            self.__log_to_file(log)

        return val

    def info(self, name, val=None):
        if self.log_level <= logging.INFO:
            log = self.__format_log(name, val)
            self.logger.info(log)
            self.__log_to_file(log)

        return val

    def debug(self, name, val=None):
        if self.log_level <= logging.DEBUG:
            log = self.__format_log(name, val)
            self.logger.debug(log)
            self.__log_to_file(log)

        return val


class ColoredFormatter(logging.Formatter):
    # These colors may seem strange.
    # That's because they're more pleasant to look at in this order.
    # Sorry not sorry.
    COLORS = {
        logging.DEBUG: '\033[36m',  # Cyan
        logging.INFO: '\033[33m',  # Yellow
        logging.WARNING: '\033[32m',  # Green
        logging.ERROR: '\033[31m',  # Red
        logging.CRITICAL: '\033[1;41m',  # White on Red
    }

    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f'{color}{message}{self.RESET}'
