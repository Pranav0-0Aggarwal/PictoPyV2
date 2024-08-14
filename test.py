import logging
import logging.config
import sys
import os

def logPath() -> str:
    """
    Log file is created in the user's home directory.

    Returns:
        str: The path to the log file.
    """
    return os.path.join(dataDir(), "log.txt")


def dataDir() -> str:
    """
    Data directory is created in the user's home directory.

    Returns:
        str: The path to the data directory.
    """
    directory = os.path.join(os.path.expanduser("~"), ".pictopy")
    os.makedirs(directory, exist_ok=True)
    return directory


class StreamToLogger(object):
    """
    Custom stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass  # StreamHandler does not require flush implementation


class LoggerHandler(logging.Handler):
    """
    A custom logging handler that emits logs to the StreamToLogger.
    """
    def __init__(self, stream_logger):
        super().__init__()
        self.stream_logger = stream_logger

    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream_logger.write(msg + '\n')
        except Exception:
            self.handleError(record)

    def flush(self):
        """
        Ensure that any buffered output has been flushed.
        """
        self.stream_logger.flush()


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'console': {
            'format': '[%(levelname)s] %(message)s',
        },
        "standard": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,  # Output to stdout
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logPath(),
            "maxBytes": 15 * 1024,  # 15 MB for testing
            "backupCount": 10,
            "delay":True,
            "mode": 'w',
        },
    },
    "loggers": {
        "": {  # Root logger
            "level": "DEBUG",
            "handlers": ["default", "file"],
        },
    },
}

# Example usage of logging config
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

# Redirect stdout and stderr to the logger
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

# Example log messages
logger.info("This is an info message.")
logger.error("This is an error message.")
