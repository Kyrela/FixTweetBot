import inspect
from typing import TypeVar, Any

from i18n import *
from i18n.translator import TranslationFormatter, pluralize
import discore

from database.models.TextChannel import *
from database.models.Guild import *


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
