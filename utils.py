from os.path import isfile

from i18n import *
from i18n.translator import TranslationFormatter, pluralize
import json


def t(key, **kwargs):
    """
    Translate a key with security

    :param key: The key to translate
    :param kwargs: The arguments to pass to the translation
    :return: The translated key
    """

    locale = kwargs.pop('locale', config.get('locale'))
    if translations.has(key, locale):
        return translate(key, locale=locale, **kwargs)
    else:
        resource_loader.search_translation(key, locale)
        if translations.has(key, locale):
            return translate(key, locale=locale, **kwargs)
        elif locale != config.get('fallback'):
            return t(key, locale=config.get('fallback'), **kwargs)
    if 'default' in kwargs:
        return kwargs['default']
    if config.get('error_on_missing_translation'):
        raise KeyError('key {0} not found'.format(key))
    else:
        return key


def translate(key, **kwargs):
    """
    Translate a key

    :param key: The key to translate
    :param kwargs: The arguments to pass to the translation
    :return: The translated key
    """

    locale = kwargs.pop('locale', config.get('locale'))
    translation = translations.get(key, locale=locale)
    if 'count' in kwargs:
        translation = pluralize(key, translation, kwargs['count'])
    return object_format(translation, **kwargs)


def object_format(object, **kwargs):
    """
    Format a template

    :param object: The object to format
    :param kwargs: The arguments to pass to the template
    :return: The formatted object
    """

    if isinstance(object, str):
        return TranslationFormatter(object).format(**kwargs)
    if isinstance(object, list):
        return [object_format(elem, **kwargs) for elem in object]
    if isinstance(object, dict):
        return {key: object_format(value, **kwargs) for key, value in object.items()}
    return object


def read_db() -> dict:
    """
    Read the db file
    :return: The db file
    """
    with open("db.json", encoding='utf-8') as f:
        return json.load(f)


def write_db(data: dict) -> None:
    """
    Write the db file
    :param data: The data to write
    :return: None
    """
    with open("db.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def is_fixtweet_enabled(guild_id: int, channel_id: int) -> bool:
    """
    Check if the fixtweet is enabled for a channel
    :param guild_id: The id of the guild to check
    :return: True if the fixtweet is enabled, False otherwise
    """

    guild = str(guild_id)
    channel = str(channel_id)

    data = read_db()
    if guild in data["guilds"].keys() and channel in data["guilds"][guild]["channels"].keys():
        return data["guilds"][guild]["channels"][channel]["fixtweet"]
    if guild in data["guilds"].keys():
        data["guilds"][guild]["channels"][channel] = {
            "fixtweet": True,
        }
    else:
        data["guilds"][guild] = {
            "channels": {
                channel: {
                    "fixtweet": True,
                }
            }
        }
    write_db(data)
    return True


def create_db() -> None:
    """
    Create the db file
    :return: None
    """
    if not isfile("db.json"):
        write_db({
            "guilds": {}
        })
