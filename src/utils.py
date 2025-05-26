import inspect
from typing import TypeVar, Any, Optional, Iterable

from discord.app_commands import locale_str
from i18n import *
import i18n
from i18n.translator import TranslationFormatter, pluralize
import discore


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
        elif 'default' in kwargs:
            return kwargs['default']
        elif locale != config.get('fallback'):
            return t(key, locale=config.get('fallback'), **kwargs)
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


V = TypeVar('V', bound='discore.ui.View', covariant=True)
I = TypeVar('I', bound='discore.ui.Item[discore.ui.View]')


def edit_callback(item: I, view: V, callback: discore.ui.item.ItemCallbackType[Any, Any]) -> I:
    """
    Edit the callback of an item
    :param item: The item to add the callback to
    :param view: The view in which the item is
    :param callback: The callback to add
    :return: The item
    """
    if not inspect.iscoroutinefunction(callback):
        raise TypeError('item callback must be a coroutine function')

    item.callback = discore.ui.view._ViewCallback(callback, view, item)
    setattr(view, callback.__name__, item)
    return item


def is_premium(i: discore.Interaction) -> Optional[bool]:
    """
    Check if the user is premium
    :param i: The interaction
    :return: True if the user is premium, False otherwise. None if no sku is registered
    """
    if not is_sku():
        return None
    if discore.config.sku is True:
        return True
    entitlement = next((
        entitlement for entitlement in i.entitlements
        if entitlement.sku_id == discore.config.sku), None)
    if entitlement is None:
        return False
    return not entitlement.is_expired()


def is_sku() -> bool:
    """
    Check if the bot has a sku
    :return: True if the bot has a sku, False otherwise
    """
    return bool(discore.config.sku)


def format_perms(
        perms: Iterable[str],
        channel: discore.TextChannel | discore.Thread,
        include_label: bool = True,
        include_valid: bool = False
) -> str:
    """
    Check for permissions in channel and format them into a human readable string

    :param perms: The permissions to check for
    :param channel: The channel to check the permissions in
    :param include_label: Whether to include the 'permission' label in the formatted permissions
    :param include_valid: Whether to include the permissions that are already given to the bot (valid)
    :return: The formatted permissions
    """

    if not perms:
        return ''
    channel_permissions = channel.permissions_for(channel.guild.me)
    guild_permissions = channel.guild.me.guild_permissions
    str_perms = "\n".join([
        '- ' + t(f'settings.perms.{perm}.{str(perm_value := getattr(channel_permissions, perm)).lower()}')
        + ('' if perm_value else t(
            'settings.perms.scope', scope=(
                channel.mention
                if getattr(guild_permissions, perm)
                else f"`{discore.utils.escape_markdown(channel.guild.name, as_needed=True)}`")
        ))
        for perm in perms
        if include_valid or not getattr(channel_permissions, perm)
    ])
    if include_label and str_perms:
        return t(
            'settings.perms.label' if include_valid else 'settings.perms.missing_label',
            channel=channel.mention) + str_perms
    return str_perms

def is_missing_perm(perms: Iterable[str], channel: discore.TextChannel | discore.Thread) -> bool:
    """
    Check for missing permissions in channel

    :param perms: The permissions to check for
    :param channel: The channel to check the permissions in
    :return: True if a permission is missing, False otherwise
    """

    if not perms:
        return False
    channel_permissions = channel.permissions_for(channel.guild.me)
    return any(not getattr(channel_permissions, perm) for perm in perms)


class I18nTranslator(discore.app_commands.Translator):
    """
    A translator that uses the i18n module
    """

    async def translate(self, locale_str: discore.app_commands.locale_str, locale: discore.Locale, _):
        # noinspection PyUnresolvedReferences
        return t(locale=locale.value, default=None, **locale_str.extras)


def tstr(key: str, **kwargs) -> locale_str:
    """
    Generate a locale_str with default message

    :param key: The key to translate
    :param kwargs: The arguments to pass to the translation
    :return: The locale_str
    """

    return locale_str(t(key, locale=i18n.config.get('fallback'), **kwargs), key=key, **kwargs)

def group_join(l: list[str], max_group_size: int, sep: str = "\n") -> list[str]:
    """
    Group items from a list into strings based on a maximum group size and a separator.

    This function takes a list of strings and combines them into groups of strings, where each group
    contains up to a specified maximum number of characters. Groups are formed by concatenating items
    from the list with a specified separator. This is useful for formatting output or preparing
    blocks of text with size constraints.

    :param l: The list of strings to group.
    :param max_group_size: The maximum allowed size (in characters) for each group.
    :param sep: The separator to use between items in a group. Default is a newline character.
    :return: A list of grouped strings, each string formed by concatenating items from the input
             list while adhering to the maximum group size constraint.
    """

    groups = []
    for item in l:
        if not groups:
            groups.append(item)
        elif len(groups[-1]) + len(sep) + len(item) <= max_group_size:
            groups[-1] += sep + item
        else:
            groups.append(item)

    return groups
