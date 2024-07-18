import logging

import discore

from masoniteorm.connections import ConnectionResolver

if not discore.config.loaded:
    discore.config_init()

DB = ConnectionResolver().set_connection_details({
    "default": "main",
    "main": discore.config.database
})

logger = logging.getLogger('masoniteorm.connection.queries')
logger.setLevel(logging.DEBUG)
