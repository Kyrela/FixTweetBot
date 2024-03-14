import os
from os import path

import addict
import yamlenv
import i18n
from i18n.translator import TranslationFormatter, pluralize

from database.models.TextChannel import TextChannel
from database.models.Guild import Guild

from dotenv import load_dotenv

import discord

config: addict.Dict = addict.Dict(loaded=False)


def config_init(**kwargs):
    """
    Initialize the configuration
    """

    env_file = kwargs.pop('env_file', '.env')
    if env_file:
        load_dotenv(dotenv_path=env_file)

    config_files = []

    if "config.yml" in os.listdir() and os.path.isfile("config.yml"):
        config_files.append("config.yml")

    if "override.config.yml" in os.listdir() and os.path.isfile("override.config.yml"):
        config_files.append("override.config.yml")

    if 'configuration_file' in kwargs:
        kwargs_config = kwargs.pop('configuration_file')
        if isinstance(kwargs_config, list):
            config_files.extend(kwargs_config)
        else:
            config_files.append(kwargs_config)

    if 'DISCORE_CONFIG' in os.environ:
        env_config = os.environ['DISCORE_CONFIG']
        if ':' in env_config:
            config_files.extend(env_config.split(':'))
        else:
            config_files.append(env_config)

    for config_file in config_files:
        with open(config_file, encoding='utf-8') as f:
            load_config(yamlenv.load(f))

    if 'configuration' in kwargs:
        load_config(kwargs.pop('configuration'))

    config.loaded = True


def load_config(configuration: dict, recursion_key: str = "override_config"):
    """
    Load a configuration given a dictionary
    """

    global config

    config.update(addict.Dict(configuration))

    if not recursion_key or recursion_key not in config:
        return

    override = config.pop(recursion_key)
    with open(override, encoding='utf-8') as f:
        load_config(yamlenv.load(f))


def sanitize(text: str, limit=4000, crop_at_end: bool = True, replace_newline: bool = True) -> str:
    """
    Sanitize a string to be displayed in Discord, and shorten it if needed

    :param text: The text to sanitize
    :param limit: The maximum length of the text
    :param crop_at_end: Whether to crop the text at the end or at the start
    :param replace_newline: Whether to replace newlines with "\\n"
    """

    sanitized_text = text.replace("```", "'''")
    if replace_newline:
        sanitized_text = sanitized_text.replace("\n", "\\n")
    text_len = len(sanitized_text)
    if text_len > limit:
        if crop_at_end:
            return sanitized_text[:limit - 3] + "..."
        return "..." + sanitized_text[text_len - limit + 3:]
    return sanitized_text


def set_embed_footer(
        bot: discord.Client, embed: discord.Embed, set_color: bool = True) -> None:
    """
    Sets the footer of an embed to the bot's name, avatar, color and version

    :param bot: The bot instance
    :param embed: The embed to set the footer of
    :param set_color: Whether to set the color of the embed to the bot's color or not
    :return: None
    """

    embed.set_footer(
        text=bot.user.name + (
            f" | ver. {config.version}" if config.version else ""),
        icon_url=bot.user.display_avatar.url
    )
    if set_color and (embed.colour is None) and config.color:
        embed.colour = config.color


def i18n_init(**kwargs):
    """
    Initialize the i18n system
    """

    i18n.set('filename_format', kwargs.pop('filename_format', '{locale}.{format}'))
    i18n.set('skip_locale_root_data', kwargs.pop('skip_locale_root_data', True))
    i18n.set('file_format', kwargs.pop('file_format', 'yml'))
    i18n.set('locale', kwargs.pop('locale', config.locale))
    i18n.set('fallback', kwargs.pop('fallback', config.locale))
    i18n.set('enable_memoization', kwargs.pop('enable_memoization', not config.hot_reload))
    locale_dir = kwargs.pop('locale_dir', 'locales')
    if path.exists(locale_dir) and path.isdir(locale_dir):
        i18n.load_path.append(locale_dir)


def t(key, **kwargs):
    """
    Translate a key with security

    :param key: The key to translate
    :param kwargs: The arguments to pass to the translation
    :return: The translated key
    """

    locale = kwargs.pop('locale', i18n.config.get('locale'))
    if i18n.translations.has(key, locale):
        return translate(key, locale=locale, **kwargs)
    else:
        i18n.resource_loader.search_translation(key, locale)
        if i18n.translations.has(key, locale):
            return translate(key, locale=locale, **kwargs)
        elif locale != i18n.config.get('fallback'):
            return t(key, locale=i18n.config.get('fallback'), **kwargs)
    if 'default' in kwargs:
        return kwargs['default']
    if i18n.config.get('error_on_missing_translation'):
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

    locale = kwargs.pop('locale', i18n.config.get('locale'))
    translation = i18n.translations.get(key, locale=locale)
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
