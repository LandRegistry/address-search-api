import logging
import atexit
import os

from service.server import app


LOGGER = logging.getLogger(__name__)


@atexit.register
def handle_shutdown(*args, **kwargs):
    LOGGER.info('Stopped the server')


LOGGER.info('Starting the server')
app.run(host='0.0.0.0', port=int(os.environ.get('PORT') or '5000'))
