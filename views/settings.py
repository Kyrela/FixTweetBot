from __future__ import annotations
import asyncio
from typing import Optional, Type, List, Self, Iterable, overload
import datetime as dt

import discore

from utils import *

__all__ = ('SettingsView',)


class BaseSetting:
    """
    Represents a bot setting
    """

    name: str
    id: str
    description: str
    emoji: Optional[str]

    async def build_embed(self, bot: discore.Bot) -> discore.Embed:
        """
        Build the setting embed
        :return: The embed
        """
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}" if self.emoji else t(self.name),
            description=t(self.description)
        )
        discore.set_embed_footer(bot, embed)
        return embed

    async def build_option(self, selected: bool) -> discore.SelectOption:
        """
        Build the setting option
        :return: The option
        """
        return discore.SelectOption(
            label=t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji,
            default=selected
        )

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        """
        Build the setting action
        :return: The action
        """
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary,
            label=t(self.name),
            custom_id=self.id
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        """
        The action to perform when the setting is selected
        :param view: The view
        :param interaction: The interaction
        :param button: The button
        """
        raise NotImplementedError

    @classmethod
    def cls_from_id(cls, id: str) -> Type[BaseSetting] | None:
        """
        Select a setting from its id
        :param id: The setting id
        :return: The setting or None if not found
        """
        for setting in cls.__subclasses__():
            if setting.id == id:
                return setting
        return None

    @staticmethod
    def dict_from_settings(settings: Iterable[BaseSetting | Type[BaseSetting]]) -> dict[str, BaseSetting]:
        """
        Create a dictionary from a list of classes
        :param settings: The list of classes
        :return: The dictionary
        """
        return {s.id: (s() if isinstance(s, type) else s) for s in settings}

    @overload
    def __eq__(self, other: str) -> bool:
        return self.id == other

    @overload
    def __eq__(self, other: BaseSetting) -> bool:
        return self.id == other.id

    def __eq__(self, other) -> bool:
        raise TypeError(f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}")

    def __hash__(self) -> int:
        return hash(self.id)


class ClickerSetting(BaseSetting):
    """
    Represents a clicker setting (for testing purposes)
    """

    name = 'Clicker'
    id = 'clicker'
    description = 'A simple clicker game'
    emoji = '👆'

    def __init__(self):
        self.counter = 0

    async def build_embed(self, bot: discore.Bot) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {self.name}",
            description=self.description + (
                f'\n**You clicked {self.counter} times**' if self.counter > 0 else ''
            )
        )
        discore.set_embed_footer(bot, embed)
        return embed

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary,
            label=f'{self.name} ({self.counter})',
            custom_id=self.id
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.counter += 1
        await view.refresh(interaction)


class ToggleSetting(BaseSetting):
    """
    Represents a toggle setting (for testing purposes)
    """

    name = 'Toggle'
    id = 'toggle'
    description = 'Toggle the setting'
    emoji = '🔄'

    def __init__(self):
        self.state = False

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.green if self.state else discore.ButtonStyle.red,
            label=f'{self.name} {"ON" if self.state else "OFF"}',
            custom_id=self.id
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        await view.refresh(interaction)


class ChannelSetting(BaseSetting):
    """
    Represents the fixtweet setting
    """

    name = 'settings.channel.name'
    id = 'channel'
    description = 'settings.channel.description'
    emoji = '#️⃣'

    def __init__(self, channel: discore.TextChannel | discore.Thread):
        self.db_channel = TextChannel.find_or_create(channel.guild.id, channel.id)
        self.state = self.db_channel.enabled
        self.channel = channel

    async def build_embed(self, bot: discore.Bot) -> discore.Embed:
        channel_permissions = self.channel.permissions_for(self.channel.guild.me)
        perms = {
            'read': channel_permissions.read_messages,
            'send': channel_permissions.send_messages,
            'embed': channel_permissions.embed_links,
            'manage': channel_permissions.manage_messages,
            'read_history': channel_permissions.read_message_history
        }
        if isinstance(self.channel, discore.Thread):
            perms['send_threads'] = channel_permissions.send_messages_in_threads
        str_perms = "\n".join([
            t(f'settings.perms.{perm}.{str(value).lower()}')
            for perm, value in perms.items()
        ])
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.channel.content',
                channel=self.channel.mention,
                bot=bot.user.display_name,
                state=t(
                    f'settings.channel.state.{str(self.state).lower()}',
                    channel=self.channel.mention,
                    bot=bot.user.display_name
                )
            ) + str_perms
        )
        discore.set_embed_footer(bot, embed)
        return embed

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.channel.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        self.db_channel.update({'enabled': self.state})
        await view.refresh(interaction)


class OriginalMessageBehaviorSetting(BaseSetting):
    """
    Represents the original message behavior setting (delete, remove embeds or nothing)
    """

    name = 'settings.original_message.name'
    id = 'original_message'
    description = 'settings.original_message.description'
    emoji = '💬'

    def __init__(self, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.state = db_guild.original_message

    async def build_embed(self, bot: discore.Bot) -> discore.Embed:
        channel_permissions = self.channel.permissions_for(self.channel.guild.me)
        perms = {
            'manage': channel_permissions.manage_messages
        }
        str_perms = "\n".join([
            t(f'settings.perms.{perm}.{str(value).lower()}')
            for perm, value in perms.items()
        ])
        option_tr_path = f'settings.original_message.option.{self.state.name.lower()}'
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.original_message.content',
                state=t(option_tr_path + '.emoji') + ' ' + t(option_tr_path + '.label'),
                channel=self.channel.mention
            ) + str_perms
        )
        discore.set_embed_footer(bot, embed)
        return embed

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        item = discore.ui.Select(
            options=[
                discore.SelectOption(
                    label=t(f'settings.original_message.option.{option.name.lower()}.label'),
                    emoji=t(f'settings.original_message.option.{option.name.lower()}.emoji'),
                    value=option.name,
                    default=option == self.state,
                )
                for option in OriginalMessage
            ]
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.state = OriginalMessage[select.values[0]]
        self.db_guild.update({'original_message': self.state.value})  # not supposed to be a string, but the convert
        # class is not working as intended (masonite issue)
        await view.refresh(interaction)


class ReplyMethodSetting(BaseSetting):
    """
    Represents the reply method setting (reply, or send)
    """

    name = 'settings.reply_method.name'
    id = 'reply_method'
    description = 'settings.reply_method.description'
    emoji = '↪️'

    def __init__(self, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.state = db_guild.reply

    async def build_embed(self, bot: discore.Bot) -> discore.Embed:
        channel_permissions = self.channel.permissions_for(self.channel.guild.me)
        perms = {
            'send': channel_permissions.send_messages,
            'read_history': channel_permissions.read_message_history,
        }
        str_perms = "\n".join([
            t(f'settings.perms.{perm}.{str(value).lower()}')
            for perm, value in perms.items()
        ])
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.reply_method.content',
                channel=self.channel.mention,
                state=t(f'settings.reply_method.state.{str(self.state).lower()}')
            ) + str_perms
        )
        discore.set_embed_footer(bot, embed)
        return embed

    async def build_action(self, view: SettingsView) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.reply_method.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        self.db_guild.update({'reply': self.state})
        await view.refresh(interaction)


class SettingsView(discore.ui.View):

    def __init__(self, i: discore.Interaction, channel: discore.TextChannel | discore.Thread):
        super().__init__()

        self.selected: Optional[Type[BaseSetting]] = None
        self.bot: discore.Bot = i.client
        self.channel: discore.TextChannel | discore.Thread = channel
        self.embed: Optional[discore.Embed] = None
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            ChannelSetting(channel),
            OriginalMessageBehaviorSetting(channel),
            ReplyMethodSetting(channel),
        ))
        self.selected_id: Optional[str] = None
        self.timeout_task: Optional[asyncio.Task] = None

    async def build(self) -> Self:
        """
        Build the interaction response (items and embed)
        :return: self
        """
        await self._build_items()
        default_embed = discore.Embed(
            title=t('settings.title'),
            description=t('settings.description')
        )
        discore.set_embed_footer(self.bot, default_embed)
        self.embed = await self.settings[self.selected_id].build_embed(self.bot) if self.selected_id else default_embed
        return self

    async def _build_items(self) -> Self:
        """
        Build the view items
        :return: self
        """
        self.clear_items()

        if self.selected_id is not None:
            for i in await self.settings[self.selected_id].build_action(self):
                self.add_item(i)

        options = [
            await self.settings[setting_id].build_option(setting_id == self.selected_id)
            for setting_id in self.settings]

        parameter_selection = discore.ui.Select(options=options)
        edit_callback(parameter_selection, self, self.__class__.select_parameter)
        self.add_item(parameter_selection)
        return self

    @staticmethod
    async def _message_delete_after(interaction: discore.Interaction, delay: float = 180.0) -> None:
        """
        Task. Automatically delete the interaction response after a delay.
        If the response is already deleted, the function will silently fail.
        This task can be cancelled by calling the cancel() method on the task object.

        :param interaction: The interaction to delete the response of
        :param delay: The delay before deleting the response
        :return: None
        """
        try:
            await asyncio.sleep(delay)
            await interaction.delete_original_response()
        except (discore.HTTPException, asyncio.CancelledError):
            pass

    async def select_parameter(self, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        """
        The callback for the select parameter item. Allows to select a setting among the available ones.
        :param interaction: The interaction to respond to
        :param select: The select parameter item
        :return: None
        """

        self.selected_id = select.values[0]
        await self.refresh(interaction)

    async def refresh(self, interaction: discore.Interaction) -> None:
        """
        Send or refresh the built view (if already sent) with the current settings
        :param interaction: The interaction to respond to
        :return: None
        """
        await self.build()

        if interaction.message is not None:
            await interaction.response.edit_message(
                view=self, embed=self.embed)
        else:
            await interaction.response.send_message(
                view=self, embed=self.embed, ephemeral=True)

        if self.timeout_task is not None:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self._message_delete_after(interaction))

    send = refresh
