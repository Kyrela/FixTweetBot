import discore

from masoniteorm.connections import ConnectionResolver

if not discore.config.loaded:
    discore.config_init()
discore.logging_init()

DB = ConnectionResolver().set_connection_details({
    "default": "main",
    "main": discore.config.database
})
