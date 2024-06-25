"""
Settings view for the bot
"""

from __future__ import annotations
import asyncio
from typing import Type, List, Self, Iterable, overload

from database.models.TextChannel import *
from database.models.Guild import *
from database.models.Member import *

from src.utils import *

__all__ = ('SettingsView',)


class BaseSetting:
    """
    Represents a bot setting
    """

    name: str
    id: str
    description: str
    emoji: Optional[str]
    fallback_emoji: Optional[str]

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.interaction: discore.Interaction = interaction
        self.bot: discore.Bot = interaction.client
        self.view: SettingsView = view

    @property
    async def embed(self) -> discore.Embed:
        """
        Build the setting embed
        :return: The embed
        """
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}" if self.emoji else t(self.name),
            description=t(self.description)
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        """
        Build the setting option
        :return: The option
        """
        return discore.SelectOption(
            label=t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def items(self) -> List[discore.ui.Item]:
        """
        Build the setting action
        :return: The action
        """
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary,
            label=t(self.name),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, item: discore.ui.Item) -> None:
        """
        The action to perform when the setting is selected
        :param view: The view
        :param interaction: The interaction
        :param item: The button
        """
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
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
    def dict_from_settings(settings: Iterable[BaseSetting]) -> dict[str, BaseSetting]:
        """
        Create a dictionary from a list of classes
        :param settings: The list of classes
        :return: The dictionary
        """
        return {s.id: s for s in settings}

    @property
    def display_emoji(self) -> str:
        """
        Get the display emoji for the setting
        :return: The emoji
        """
        channel = self.interaction.channel
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.use_external_emojis:
            return self.fallback_emoji or self.emoji or ''
        return self.emoji or self.fallback_emoji or ''

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

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.counter = 0
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {self.name}",
            description=self.description + (
                f'\n**You clicked {self.counter} times**' if self.counter > 0 else ''
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary,
            label=f'{self.name} ({self.counter})',
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.state = False
        super().__init__(interaction, view)

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.green if self.state else discore.ButtonStyle.red,
            label=f'{self.name} {"ON" if self.state else "OFF"}',
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
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

    def __init__(
            self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel | discore.Thread):
        self.db_channel = TextChannel.find_or_create(channel.guild.id, channel.id)
        self.state = self.db_channel.enabled
        self.channel = channel
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
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
                bot=self.bot.user.display_name,
                state=t(
                    f'settings.channel.state.{str(self.state).lower()}',
                    channel=self.channel.mention,
                    bot=self.bot.user.display_name
                )
            ) + str_perms
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.channel.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.state = db_guild.original_message
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
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
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
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
        edit_callback(item, self.view, self.action)
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
    emoji = discore.config.emoji.reply
    fallback_emoji = '↪️'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.state = db_guild.reply
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
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
            title=f"{self.display_emoji} {t(self.name)}",
            description=t(
                'settings.reply_method.content',
                channel=self.channel.mention,
                state=t(f'settings.reply_method.state.{str(self.state).lower()}', emoji=self.display_emoji)
            ) + str_perms
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.reply_method.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        self.db_guild.update({'reply': self.state})
        await view.refresh(interaction)


class TwitterSetting(BaseSetting):
    """
    Represents the fixtweet setting
    """

    name = 'settings.twitter.name'
    id = 'twitter'
    description = 'settings.twitter.description'
    emoji = discore.config.emoji.twitter
    fallback_emoji = '🐦'

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.db_guild = Guild.find_or_create(interaction.guild.id)
        self.state = self.db_guild.twitter
        self.translation = self.db_guild.twitter_tr
        self.lang = self.db_guild.twitter_tr_lang
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.display_emoji} {t(self.name)}",
            description=t(
                'settings.twitter.content',
                state=t(
                    f'settings.twitter.state.{str(self.state).lower()}',
                    translation=t(
                        f'settings.twitter.translation.{str(self.translation).lower()}',
                        lang=self.lang
                    )
                )
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        toggle_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.twitter.button.state.{str(self.state).lower()}'),
            custom_id=self.id
        )
        translation_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.translation and self.state else discore.ButtonStyle.secondary,
            label=t(
                f'settings.twitter.button.translation.{str(self.translation and self.state).lower()}',
                lang=self.lang
            ),
            custom_id='twitter_translation',
            disabled=not self.state
        )
        edit_callback(toggle_button, self.view, self.action)
        edit_callback(translation_button, self.view, self.action)
        return [toggle_button, translation_button]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        if button.custom_id == self.id:
            self.state = not self.state
            self.db_guild.update({'twitter': self.state})
        elif button.custom_id == 'twitter_translation':
            self.translation = not self.translation
            # noinspection PyUnresolvedReferences
            self.lang = interaction.locale.value.split('-')[0]
            self.db_guild.update({'twitter_tr': self.translation, 'twitter_tr_lang': self.lang})
        await view.refresh(interaction)


class InstagramSetting(BaseSetting):
    """
    Represents the fixtweet setting
    """

    name = 'settings.instagram.name'
    id = 'instagram'
    description = 'settings.instagram.description'
    emoji = discore.config.emoji.instagram
    fallback_emoji = '📸'

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.db_guild = Guild.find_or_create(interaction.guild.id)
        self.state = self.db_guild.instagram
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.display_emoji} {t(self.name)}",
            description=t(
                'settings.instagram.content',
                state=t(f'settings.instagram.state.{str(self.state).lower()}')
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.instagram.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        self.db_guild.update({'instagram': self.state})
        await view.refresh(interaction)


class MemberSetting(BaseSetting):
    """
Represents the fixtweet setting
"""

    name = 'settings.member.name'
    id = 'member'
    description = 'settings.member.description'
    emoji = '👤'

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            channel: discore.TextChannel | discore.Thread,
            member: discore.Member
    ):
        self.db_member = Member.find_or_create(channel.guild.id, member.id)
        self.channel = channel
        self.member = member
        self.state = self.db_member.enabled
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
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
                'settings.member.content',
                member=self.member.mention,
                channel=self.channel.mention,
                bot=self.bot.user.display_name,
                state=t(
                    f'settings.member.state.{str(self.state).lower()}',
                    member=self.member.mention,
                    bot=self.bot.user.display_name
                )
            ) + str_perms
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.member.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        self.state = not self.state
        self.db_member.update({'enabled': self.state})
        await view.refresh(interaction)


class SettingsView(discore.ui.View):

    def __init__(
            self,
            i: discore.Interaction,
            channel: discore.TextChannel | discore.Thread,
            member: Optional[discore.Member]):
        super().__init__()

        self.selected: Optional[Type[BaseSetting]] = None
        self.bot: discore.Bot = i.client
        self.channel: discore.TextChannel | discore.Thread = channel
        self.member: Optional[discore.Member] = member
        self.embed: Optional[discore.Embed] = None
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            ChannelSetting(i, self, channel),
            OriginalMessageBehaviorSetting(i, self, channel),
            ReplyMethodSetting(i, self, channel),
            TwitterSetting(i, self),
            InstagramSetting(i, self),
        ))
        if self.member:
            self.settings['member'] = MemberSetting(i, self, channel, member)
        if self.member == self.bot.user:
            self.settings['clicker'] = ClickerSetting(i, self)
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
        self.embed = await self.settings[self.selected_id].embed if self.selected_id else default_embed
        return self

    async def _build_items(self) -> Self:
        """
        Build the view items
        :return: self
        """
        self.clear_items()

        if self.selected_id is not None:
            for i in await self.settings[self.selected_id].items:
                self.add_item(i)

        options = []
        for setting_id in self.settings:
            option = await self.settings[setting_id].option
            if setting_id == self.selected_id:
                option.default = True
            options.append(option)

        parameter_selection = discore.ui.Select(options=options)
        # noinspection PyTypeChecker
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
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(
                view=self, embed=self.embed)
        else:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                view=self, embed=self.embed, ephemeral=True)

        if self.timeout_task is not None:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self._message_delete_after(interaction))

    send = refresh
