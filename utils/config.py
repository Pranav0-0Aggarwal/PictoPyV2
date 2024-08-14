import os
import sys  

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
            "maxBytes": 15 * 1024 * 1024,  # 15 MB for 3 * 5 MB of backup
            "backupCount": 10,
            "delay": True,
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
