import logging
import logging.config
import logging.handlers
import sys
import os
from atexit import register
import queue
from time import time


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


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,  # Output to stdout
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logPath(),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {  # Root logger
            "level": "DEBUG",
            "handlers": ["default", "file"],
        },
    },
}


def setup_logging() -> logging.Logger:
    """
    Sets up the logging system, redirects stdout/stderr to the logger,
    and returns the logger instance.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger("app")

    # Redirect stdout and stderr to logger
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)

    # Configure the logger
    logging.config.dictConfig(LOG_CONFIG)

    log_queue = queue.Queue()
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, *logger.handlers)
    logger.addHandler(queue_handler)

    # Start the listener
    listener.start()

    # Register the listener stop to be called on exit
    register(listener.stop)

    return logger


# Example usage
if __name__ == "__main__":
    logger = setup_logging()

    # Example log messages
    start = time()
    for i in range(1000):
        logger.info(f"{i} {time() - start}")

    # Test log messages
    print("test")
