# Credit: https://github.com/thewilltejeda/htmx-desktop-app-01/blob/main/run.py

import logging
import logging.config
import queue
import sys
import webview
from threading import Thread, Event
from main import app
from utils import StreamToLogger
from config import *


# This event will be set when we need to stop the Flask server
stopEvent = Event()

appTitle = "PictoPy"
host = "http://127.0.0.1"
port = 5000

def setupLogging() -> logging.Logger:
    """
    Sets up the logging system, redirects stdout/stderr to the logger,
    and returns the listner instance.

    Logger instance isnt required since it i 

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


    return listener

def run():
    while not stopEvent.is_set():
        app.run(port=port, use_reloader=False)

if __name__ == '__main__':
    t = Thread(target=run)
    t.daemon = True  # This ensures the thread will exit when the main program exits
    t.start()
    listener = setupLogging()

    webview.create_window(
        appTitle,
        f"{host}:{port}",
        # resizable=False,
        # height=710,
        # width=225,
        # frameless=True,
        easy_drag=True
        )
    
    webview.start()

    stopEvent.set()  # Signal the Flask server to shut down

    listener.stop()
