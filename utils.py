from i18n import *
from i18n.translator import TranslationFormatter, pluralize

from database.models.TextChannel import TextChannel
from database.models.Guild import Guild


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


def is_fixtweet_enabled(guild_id: int, channel_id: int) -> bool:
    """
    Check if the fixtweet is enabled for a channel
    :return: True if the fixtweet is enabled, False otherwise
    """

    channel = TextChannel.find(channel_id)

    if channel is None:
        guild = Guild.find(guild_id)
        if guild is None:
            Guild.create({'id': guild_id})
        channel = TextChannel.create({'id': channel_id, 'guild_id': guild_id, 'fix_twitter': True})

    return channel.fix_twitter
