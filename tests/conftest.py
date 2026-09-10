import discore


def pytest_configure():
    if not discore.config.loaded:
        discore.config_init()
