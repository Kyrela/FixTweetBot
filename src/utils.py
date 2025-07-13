import inspect
from typing import TypeVar, Any, Optional, Iterable, Protocol, Generic

from discord.app_commands import locale_str
from i18n import *
import i18n
from i18n.translator import TranslationFormatter, pluralize
import discore

from database.models.DiscordRepresentation import DiscordRepresentation

__all__ = (
    't', 'translate', 'object_format', 'edit_callback', 'is_premium',
    'is_sku', 'format_perms', 'is_missing_perm', 'I18nTranslator', 'tstr',
    'group_join', 'l', 'GuildChild', 'HybridElement', 'reply_to_member'
)

from database.models.Guild import Guild

from database.models.Member import Member
from database.models.Role import Role


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

def l(e: Any) -> str:
    """
    Lowers an element

    :param e: The element to lower
    :return: The lowered element as a string
    """

    return str(e).lower()

class GuildChild(Protocol):
    """
    Protocol for Discord objects that are children of a guild.
    """

    guild: discore.Guild
    id: int

D = TypeVar('D', bound=discore.abc.Snowflake)
M = TypeVar('M', bound=DiscordRepresentation)

class HybridElement(Generic[D, M]):
    """
    A class that combines a Discord object and a database model.
    """

    def __init__(self, discord_object: D, model_class: type[M], **kwargs: Any):
        self.discord_object: D = discord_object
        self.db_object: M = model_class.find_or_create(discord_object, **kwargs)

    def replace(self, discord_object: D, **kwargs: Any) -> None:
        """
        Replace the Discord object and update the database model.
        :param discord_object: The new Discord object to replace the old one.
        :param kwargs: Additional keyword arguments to pass to the database model's update method.
        """
        self.discord_object = discord_object
        self.db_object = type(self.db_object).find_or_create(discord_object, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """
        Allow access to attributes of both the Discord object and the database model as if they were the same object.
        :param name: The name of the attribute to access.
        :return: The value of the attribute from the Discord object or the database model.
        """

        if name in ('discord_object', 'db_object', 'replace', '__repr__', '__getattr__', '__setattr__', '__getitem__', '__eq__'):
            return super().__getattr__(name)
        try:
            return getattr(self.discord_object, name)
        except AttributeError:
            pass
        try:
            return getattr(self.db_object, name)
        except AttributeError:
            pass
        return super().__getattr__(name)

    def __eq__(self, other: object) -> bool:
        if hasattr(other, 'id') and self.id == other.id:
            return True
        return False

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Allow setting attributes on both the Discord object and the database model.
        :param name: The name of the attribute to set.
        :param value: The value to set the attribute to.
        """
        if name in ('discord_object', 'db_object'):
            super().__setattr__(name, value)
            return
        if hasattr(self.discord_object, name):
            setattr(self.discord_object, name, value)
        elif hasattr(self.db_object, name):
            setattr(self.db_object, name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self) -> str:
        """
        Return a string representation of the HybridElement.
        :return: A string representation of the HybridElement.
        """
        return f"{self.__class__.__name__}(discord_object={self.discord_object!r}, db_object={self.db_object!r})"

    def __getitem__(self, item):
        return self.db_object[item]

def reply_to_member(
    guild: HybridElement[discore.Guild, Guild],
    member: HybridElement[discore.Member, Member],
    roles: list[HybridElement[discore.Role, Role]]
) -> bool:
    """
    Check if a member has any of the specified roles.

    :param guild: The guild in which the member exists.
    :param member: The member to check.
    :param roles: The list of roles to check against.
    :return: True if the member has any of the specified roles, False otherwise.
    """

    if not member.enabled(guild):
        return False
    if not (any if guild.roles_use_any_rule else all)(r.enabled(guild) for r in roles):
        return False
    return True
