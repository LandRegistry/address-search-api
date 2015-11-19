import logging
from service import logging_config

logging_config.setup_logging()
LOGGER = logging.getLogger(__name__)

# Application event handlers for when the server is run by gunicorn


def on_starting(server):
    LOGGER.info('Starting the server')


def on_reload(server):
    LOGGER.info('Reloading the server')


def when_ready(server):
    LOGGER.info('Server is ready')


def on_exit(server):
    LOGGER.info('Stopping the server')
