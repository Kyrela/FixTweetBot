"""
Settings view for the bot
"""

from __future__ import annotations
import asyncio
from typing import Type, List, overload, Iterable, Any

import discore.ui.select

from database.models.Guild import GettableEnum
from database.models.Role import Role
from database.models.TextChannel import *
from database.models.Guild import *
from database.models.Member import *
from database.models.CustomWebsite import CustomWebsite

from src.utils import *

__all__ = ('SettingsView',)


class DataElements:
    """
    Represents the database elements for the settings view
    """

    def __init__(self, interaction: discore.Interaction):
        self.guild = HybridElement(interaction.guild, Guild)
        self.member = HybridElement(interaction.user, Member, guild=self.guild)
        self.channel = HybridElement(interaction.channel, TextChannel, guild=self.guild)
        self.role = HybridElement(interaction.user.top_role, Role, guild=self.guild)
        self.roles = [HybridElement(role, Role, guild=self.guild) for role in interaction.user.roles]

    def refresh(self):
        """
        Refresh the data elements
        :return: None
        """

        self.guild.db_object = self.guild.db_object.fresh()
        self.member.db_object = self.member.db_object.fresh()
        self.channel.db_object = self.channel.db_object.fresh()
        self.role.db_object = self.role.db_object.fresh()
        self.roles.clear()
        self.roles.extend(
            HybridElement(role, Role, guild=self.guild) for role in self.member.discord_object.roles
        )


class BaseSetting:
    """
    Represents a bot setting
    """

    name: str
    id: str
    description: str
    emoji: Optional[str]

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        self.interaction: discore.Interaction = interaction
        self.bot: discore.Bot = interaction.client
        self.view: SettingsView = view
        self.ctx: DataElements = ctx

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
        Build the setting items
        :return: The items
        """
        return []

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


class WebsiteBaseSetting(BaseSetting):
    """
    Represents the website base setting
    """

    proxies: dict[str, str]
    is_view: bool = False
    is_translation: bool = False

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            ctx: DataElements,
            enum: Type[GettableEnum] = None
    ):
        super().__init__(interaction, view, ctx)
        self.state = bool(self.ctx.guild[self.id])
        self.view_state = None
        self.view_enum = None
        self.translation = None
        if self.is_view:
            self.view_state = self.ctx.guild[f'{self.id}_view']
            if enum is not None:
                self.view_enum = enum
            else:
                enum_name = f'{self.id.title()}View'
                self.view_enum = getattr(__import__('database.models.Guild', fromlist=[enum_name]), enum_name)
        if self.is_translation:
            self.translation = bool(self.ctx.guild[f'{self.id}_tr'])
            self.lang = self.ctx.guild.lang

    @property
    async def embed(self) -> discore.Embed:
        self.lang = self.ctx.guild.lang if self.is_translation else None
        embed = discore.Embed(
            title=f"{self.emoji} {self.name}",
            description=t(
                f'settings.base_website.content',
                name=self.name,
                state=t(
                    f'settings.base_website.state.{l(self.state)}',
                    name=self.name,
                    translation=(
                        t(f'settings.base_website.translation.{l(self.translation)}', lang=self.lang)
                        if self.is_translation and self.state else ''
                    )
                ),
                view=(
                        '\n' + t(f'settings.base_website.view.{self.view_state.name.lower()}.emoji')
                        + ' ' + t(f'settings.base_website.view.{self.view_state.name.lower()}.label'))
                if self.view_state else '',
                credits=t('settings.base_website.credits_separator').join(f"[{p_name}](<{p_url}>)" for p_name, p_url in self.proxies.items())
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        items = []
        self.lang = self.ctx.guild.lang if self.is_translation else None
        state_switch = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.base_website.button.state.{l(self.state)}'),
            custom_id=self.id
        )
        edit_callback(state_switch, self.view, self.action)
        items.append(state_switch)
        if self.is_translation:
            translation_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.translation and self.state else discore.ButtonStyle.secondary,
                label=t(
                    f'settings.base_website.button.translation.{l(bool(self.translation and self.state))}',
                    lang=self.lang
                ),
                custom_id=f'{self.id}_translation',
                disabled=not self.state
            )
            edit_callback(translation_button, self.view, self.translation_action)
            items.append(translation_button)
            translation_lang_button = discore.ui.Button(
                label=t('settings.base_website.button.translation_lang'),
                custom_id=f'{self.id}_translation_lang',
                disabled=not (self.translation and self.state)
            )
            edit_callback(translation_lang_button, self.view, self.translation_lang_action)
            items.append(translation_lang_button)
        if self.is_view:
            view_selector = discore.ui.Select(
                options=[
                    discore.SelectOption(
                        label=t(f'settings.base_website.view.{view.name.lower()}.label'),
                        emoji=t(f'settings.base_website.view.{view.name.lower()}.emoji'),
                        value=view.name,
                        default=view == self.view_state,
                    )
                    for view in self.view_enum
                ]
            )
            edit_callback(view_selector, self.view, self.view_action)
            items.append(view_selector)

        return items

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.ctx.guild.update({self.id: self.state})
        await view.refresh(interaction)

    async def translation_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.translation = not self.translation
        if self.ctx.guild.lang is None:
            # noinspection PyUnresolvedReferences
            self.lang = interaction.locale.value.split('-')[0]
        self.ctx.guild.update({f'{self.id}_tr': self.translation, 'lang': self.lang})
        await view.refresh(interaction)

    async def translation_lang_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        await self.view.reset_timeout(interaction)
        # noinspection PyUnresolvedReferences
        await interaction.response.send_modal(TranslationModal(self))

    async def view_action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        if not self.is_view:
            await view.refresh(interaction)
            return
        self.view_state = self.view_enum[select.values[0]]
        self.ctx.guild.update({f'{self.id}_view': self.view_state.value}, cast=False)
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + self.name,
            value=self.id,
            description=t('settings.base_website.description', name=self.name),
            emoji=self.emoji
        )


class TranslationModal(discore.ui.Modal):
    def __init__(self, setting: BaseSetting, **kwargs):
        """
        Modal for changing the language setting of the guild
        :param setting: The setting to change the language for
        :param kwargs: Additional keyword arguments for the modal
        """
        
        super().__init__(
            title=t('settings.lang_modal.title'),
            timeout=180,
            **kwargs
        )
        self.setting = setting
        # noinspection PyUnresolvedReferences
        self.lang = setting.ctx.guild.lang
        # noinspection PyUnresolvedReferences
        self.add_item(discore.ui.TextInput(
            label=t('settings.lang_modal.label'),
            placeholder=t('settings.lang_modal.placeholder'),
            custom_id='lang',
            default=self.lang
        ))

    async def on_submit(self, interaction: discore.Interaction):
        lang = str(self.children[0])
        if len(lang) != 2:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                t('settings.lang_modal.error', lang=lang), ephemeral=True, delete_after=10)
            return
        self.setting.ctx.guild.update({'lang': lang})
        await self.setting.view.refresh(interaction)


class EmbedEZBaseSetting(WebsiteBaseSetting):
    """
    Represents the EmbedEZ base setting
    """

    proxies = {"EmbedEZ": "https://embedez.com"}
    is_view = True
    is_translation = True

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx, enum=EmbedEzView)


class ClickerSetting(BaseSetting):
    """
    Represents a clicker setting (for testing purposes)
    """

    name = 'Clicker'
    id = 'clicker'
    description = 'A simple clicker game'
    emoji = '👆'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.counter = 0

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

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.state = False

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.green if self.state else discore.ButtonStyle.red,
            label=f'{self.name} {"ON" if self.state else "OFF"}',
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        await view.refresh(interaction)


class TroubleshootingSetting(BaseSetting):
    """
    Represents the troubleshooting setting
    """

    name = 'settings.troubleshooting.name'
    id = 'troubleshooting'
    description = 'settings.troubleshooting.description'
    emoji = '🛠️'

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t('settings.troubleshooting.description')
        )
        embed.add_field(
            name=t('settings.troubleshooting.ping.name'),
            value=t('settings.troubleshooting.ping.value', latency=format(self.bot.latency * 1000, '.0f')),
            inline=False
        )
        perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(self.ctx.channel.discord_object, discore.Thread):
            perms.append('send_messages_in_threads')
        if self.ctx.guild.original_message != OriginalMessage.NOTHING:
            perms.append('manage_messages')
        if self.ctx.guild.reply_to_message:
            perms.append('read_message_history')
        embed.add_field(
            name=t('settings.troubleshooting.permissions', channel=self.ctx.channel.mention),
            value=format_perms(perms, self.ctx.channel.discord_object, include_label=False, include_valid=True),
            inline=False
        )
        # (id, display_value, state, indented)
        options = [
            ('channels', self.ctx.channel.mention, self.ctx.channel.enabled(self.ctx.guild), False),
            ('webhooks', None, self.ctx.guild.db_object.webhooks, False),
            ('member', self.ctx.member.mention, reply_to_member(self.ctx.guild, self.ctx.member, self.ctx.roles), False),
            ('members', self.ctx.member.mention, self.ctx.member.enabled(self.ctx.guild), True),
        ]
        options.extend(
            ('roles', role.mention, role.enabled(self.ctx.guild), True)
            for role in self.ctx.roles
        )
        options.extend(
            ('keywords', keyword, self.ctx.guild.keywords_use_allow_list, False)
            for keyword in self.ctx.guild.keywords
        )

        str_options_fields = group_join(
            (
                ('  - ' if indented else '- ') + t(f'settings.{id}.state.{l(state)}',
                         **{'element': display_value, 'details': ''})
                for id, display_value, state, indented in options),
            1024
        )

        for i, str_options in enumerate(str_options_fields):
            embed.add_field(
                name=t('settings.troubleshooting.filters') + (f' ({i+1})' if i+1 > 1 else ''),
                value=str_options,
                inline=False
            )

        websites = {
            'twitter': 'Twitter',
            'instagram': 'Instagram',
            'tiktok': 'TikTok',
            'reddit': 'Reddit',
            'threads': 'Threads',
            'bluesky': 'Bluesky',
            'snapchat': 'Snapchat',
            'facebook': 'Facebook',
            'pinterest': 'Pinterest',
            'pixiv': 'Pixiv',
            'twitch': 'Twitch',
            'spotify': 'Spotify',
            'deviantart': 'DeviantArt',
            'mastodon': 'Mastodon',
            'tumblr': 'Tumblr',
            'bilibili': 'BiliBili',
            'ifunny': 'iFunny',
            'furaffinity': 'Fur Affinity',
            'youtube': 'YouTube',
            'imageboards': 'Imageboards',
        }
        str_websites = "\n".join([
            '- ' + t(
                f'settings.base_website.state.{l(bool(self.ctx.guild[key]))}',
                name=value, translation=''
            )
            for key, value in websites.items()
        ])
        embed.add_field(
            name=t('settings.troubleshooting.websites'),
            value=str_websites,
            inline=False
        )
        if self.ctx.guild.custom_websites:
            str_custom_websites = "\n".join([
                f"- `{website.domain}`"
                for website in self.ctx.guild.custom_websites
            ])
            embed.add_field(
                name=t('settings.troubleshooting.custom_websites'),
                value=str_custom_websites,
                inline=False
            )
        embed.add_field(
            name=t('settings.troubleshooting.premium.name'),
            value=t(f'settings.troubleshooting.premium.{l(bool(is_premium(self.interaction)))}'),
            inline=False)
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        refresh_button = discore.ui.Button(
            label=t('settings.troubleshooting.refresh')
        )
        edit_callback(refresh_button, self.view, self.refresh_action)
        premium_button = discore.ui.Button(
            style=discore.ButtonStyle.premium,
            sku_id=discore.config.sku
        )
        support = discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.support'),
            url=discore.config.support_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.discord)
        )
        # noinspection PyTypeChecker
        select_channel = discore.ui.ChannelSelect(
            custom_id=f'channel_select',
            default_values=[self.ctx.channel.discord_object],
            placeholder=t(f'settings.channels.select'),
            channel_types=[
                discore.ChannelType.text,
                discore.ChannelType.voice,
                discore.ChannelType.news,
                discore.ChannelType.stage_voice,
                discore.ChannelType.news_thread,
                discore.ChannelType.public_thread,
                discore.ChannelType.private_thread,
            ]
        )
        edit_callback(select_channel, self.view, self.select_channel_action)
        select_member = discore.ui.UserSelect(
            custom_id=f'member_select',
            default_values=[self.ctx.member.discord_object],
            placeholder=t(f'settings.members.select')
        )
        edit_callback(select_member, self.view, self.select_member_action)
        return (
            [refresh_button, support, select_channel, select_member]
            if is_premium(self.interaction) or not is_sku()
            else [refresh_button, premium_button, support, select_channel, select_member]
        )

    async def refresh_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.interaction = interaction
        self.ctx.refresh()
        await view.refresh(interaction)

    async def select_channel_action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.ChannelSelect) -> None:
        channel = select.values[0]
        if isinstance(channel, discore.app_commands.AppCommandChannel) or isinstance(channel, discore.app_commands.AppCommandThread):
            channel = channel.resolve()
        self.ctx.channel.replace(channel, guild=self.ctx.guild)
        await view.refresh(interaction)

    async def select_member_action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.UserSelect) -> None:
        self.ctx.member.replace(select.values[0], guild=self.ctx.guild)
        self.ctx.roles.clear()
        self.ctx.roles.extend(
            HybridElement(role, Role, guild=self.ctx.guild) for role in self.ctx.member.discord_object.roles
        )
        await view.refresh(interaction)


class GenericFilterSetting(BaseSetting):
    """
    Represents a generic filter setting
    """

    Model: Type[AFilterModel]
    data_name: str
    Select: Type[discore.ui.ChannelSelect | discore.ui.RoleSelect | discore.ui.UserSelect]
    select_kwargs: dict[str, Any] = {}

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            ctx: DataElements
    ):
        super().__init__(interaction, view, ctx)
        self.element = ctx.__getattribute__(self.data_name)
        self.enabled = self.element.enabled(self.ctx.guild)
        self.db_list_column = f'{self.Model.__table__}_use_allow_list'
        self.use_deny_list = not bool(self.ctx.guild[self.db_list_column])
        self.reset_clicked_level = 0
        self.perms: list[str] = []

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=
            t(f'settings.{self.id}.content',
              bot=self.bot.user.display_name,
              element=self.element.mention,
              state=t(f'settings.{self.id}.state.{l(self.enabled)}',
                        element=self.element.mention,
                      details=t(f'settings.filters.labels.details.on_list.{l(self.element.on_list(self.ctx.guild))}',
                                list= t(f'settings.filters.labels.details.list.{l(self.use_deny_list)}')),
                      ),
              default_state= t(f'settings.filters.labels.default.{l(self.use_deny_list)}'),
              perms=format_perms(self.perms, self.ctx.channel.discord_object))
        )
        self.reset_clicked_level -= 1
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        toggle_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.enabled else discore.ButtonStyle.secondary,
            label=t(f'settings.filters.button.toggle.{l(self.enabled)}'),
            custom_id=f'{self.id}_toggle'
        )
        edit_callback(toggle_button, self.view, self.toggle)
        if is_premium(self.interaction):
            toggle_default_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.use_deny_list else discore.ButtonStyle.secondary,
                label=t(f'settings.filters.button.toggle_default.{l(self.use_deny_list)}'),
                custom_id=f'{self.id}_default'
            )
        else:
            toggle_default_button = discore.ui.Button(
                label=t('settings.filters.button.toggle_default.premium'),
                disabled=True
            )
        edit_callback(toggle_default_button, self.view, self.toggle_default)
        reset_button = discore.ui.Button(
            style=discore.ButtonStyle.danger,
            label=t(f'settings.filters.button.reset.{l(self.reset_clicked_level > 1)}'),
            custom_id=f'{self.id}_reset'
        )
        edit_callback(reset_button, self.view, self.reset)
        selector = self.Select(
            custom_id=f'{self.id}_select',
            default_values=[self.element.discord_object],
            placeholder=t(f'settings.{self.id}.select'),
            **self.select_kwargs
        )
        edit_callback(selector, self.view, self.select_element)
        return [toggle_button, toggle_default_button, reset_button, selector]

    async def toggle(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.enabled = not self.enabled
        self.element.update_enabled(self.enabled, self.ctx.guild)
        await view.refresh(interaction)

    async def toggle_default(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if not is_premium(interaction):
            await view.refresh(interaction)
            return
        self.use_deny_list = not self.use_deny_list
        self.ctx.guild.update({self.db_list_column: not self.use_deny_list})
        self.enabled = self.element.enabled(self.ctx.guild)
        await view.refresh(interaction)

    async def reset(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if self.reset_clicked_level <= 0:
            self.reset_clicked_level = 2
            await view.refresh(interaction)
            return

        self.reset_clicked_level = 0
        self.Model.reset_lists(self.ctx.guild.db_object)
        self.element.db_object = self.Model.find_or_create(self.element, self.ctx.guild.db_object)
        self.enabled = self.element.enabled(self.ctx.guild.db_object)
        await view.refresh(interaction)

    async def select_element(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.element.replace(select.values[0], guild=self.ctx.guild)
        self.enabled = self.element.enabled(self.ctx.guild.db_object)
        await view.refresh(interaction)


    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=(('⚠️ ' if is_missing_perm(self.perms, self.ctx.channel.discord_object) else '🟢 ')
                   if self.enabled else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )


class MemberSetting(GenericFilterSetting):
    """
    Represents the member setting
    """

    name = 'settings.members.name'
    id = 'members'
    description = 'settings.members.description'
    emoji = '👤'
    Model = Member
    data_name = 'member'
    Select = discore.ui.UserSelect

    async def select_element(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.element.replace(select.values[0], guild=self.ctx.guild)
        self.enabled = self.element.enabled(self.ctx.guild.db_object)
        self.ctx.roles.clear()
        self.ctx.roles.extend(
            HybridElement(role, Role, guild=self.ctx.guild) for role in self.ctx.member.discord_object.roles
        )
        await view.refresh(interaction)

    @property
    async def items(self) -> List[discore.ui.Item]:
        if is_premium(self.interaction) or not self.ctx.member.bot:
            toggle_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.enabled else discore.ButtonStyle.secondary,
                label=t(f'settings.filters.button.toggle.{l(self.enabled)}'),
                custom_id=f'{self.id}_toggle'
            )
        else:
            toggle_button = discore.ui.Button(
                label=t('settings.members.toggle_bot_premium'),
                disabled=True
            )
        edit_callback(toggle_button, self.view, self.toggle)
        if is_premium(self.interaction):
            toggle_default_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.use_deny_list else discore.ButtonStyle.secondary,
                label=t(f'settings.filters.button.toggle_default.{l(self.use_deny_list)}'),
                custom_id=f'{self.id}_default'
            )
        else:
            toggle_default_button = discore.ui.Button(
                label=t('settings.filters.button.toggle_default.premium'),
                disabled=True
            )
        edit_callback(toggle_default_button, self.view, self.toggle_default)
        reset_button = discore.ui.Button(
            style=discore.ButtonStyle.danger,
            label=t(f'settings.filters.button.reset.{l(self.reset_clicked_level > 1)}'),
            custom_id=f'{self.id}_reset'
        )
        edit_callback(reset_button, self.view, self.reset)
        selector = self.Select(
            custom_id=f'{self.id}_select',
            default_values=[self.element.discord_object],
            placeholder=t(f'settings.{self.id}.select'),
            **self.select_kwargs
        )
        edit_callback(selector, self.view, self.select_element)
        return [toggle_button, toggle_default_button, reset_button, selector]



class ChannelSetting(GenericFilterSetting):
    """
    Represents the channel setting
    """

    name = 'settings.channels.name'
    id = 'channels'
    description = 'settings.channels.description'
    emoji = '#️⃣'
    Model = TextChannel
    data_name = 'channel'
    Select = discore.ui.ChannelSelect
    select_kwargs = {
        'channel_types': [
            discore.ChannelType.text,
            discore.ChannelType.voice,
            discore.ChannelType.news,
            discore.ChannelType.stage_voice,
            discore.ChannelType.news_thread,
            discore.ChannelType.public_thread,
            discore.ChannelType.private_thread,
        ]
    }

    def __init__(
            self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(ctx.channel.discord_object, discore.Thread):
            self.perms.append('send_messages_in_threads')

    async def select_element(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        channel = select.values[0]
        if isinstance(channel, discore.app_commands.AppCommandChannel) or isinstance(channel, discore.app_commands.AppCommandThread):
            channel = channel.resolve()
        self.element.replace(channel, guild=self.ctx.guild)
        self.enabled = self.element.enabled(self.ctx.guild.db_object)
        await view.refresh(interaction)


class RoleSetting(GenericFilterSetting):
    name = 'settings.roles.name'
    id = 'roles'
    description = 'settings.roles.description'
    emoji = discore.config.emoji.role
    data_name = 'role'
    Model = Role
    Select = discore.ui.RoleSelect

    def __init__(
            self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.use_any_rule = ctx.guild.roles_use_any_rule

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=
            t(f'settings.{self.id}.content',
              bot=self.bot.user.display_name,
              element=self.element.mention,
              state=t(f'settings.{self.id}.state.{l(self.enabled)}',
                      element=self.element.mention,
                      details=t(f'settings.filters.labels.details.on_list.{l(self.element.on_list(self.ctx.guild))}',
                                list= t(f'settings.filters.labels.details.list.{l(self.use_deny_list)}')),
                      ),
              default_state= t(f'settings.filters.labels.default.{l(self.use_deny_list)}'),
              rule=t(f'settings.{self.id}.rule.{l(self.use_any_rule)}'),
              perms=format_perms(self.perms, self.ctx.channel.discord_object))
        )
        self.reset_clicked_level -= 1
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        if is_premium(self.interaction):
            toggle_rule_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.use_any_rule else discore.ButtonStyle.secondary,
                label=t(f'settings.{self.id}.button.rule.{l(self.use_any_rule)}'),
                custom_id=f'{self.id}_rule'
            )
        else:
            toggle_rule_button = discore.ui.Button(
                label=t(f'settings.{self.id}.button.rule.premium'),
                disabled=True
            )
        edit_callback(toggle_rule_button, self.view, self.toggle_rule)
        items = await super().items
        return [items[0], items[1], toggle_rule_button, items[2], items[3]]

    async def toggle(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.enabled = not self.enabled
        self.element.update_enabled(self.enabled, self.ctx.guild)
        try:
            idx = self.ctx.roles.index(self.element)
            self.ctx.roles[idx].db_object = self.element.db_object
        except ValueError:
            pass
        await view.refresh(interaction)

    async def toggle_rule(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if not is_premium(interaction):
            await view.refresh(interaction)
            return
        self.use_any_rule = not self.use_any_rule
        self.ctx.guild.update({'roles_use_any_rule': self.use_any_rule})
        await view.refresh(interaction)


class KeywordModal(discore.ui.Modal):

    def __init__(self, keyword_index: Optional[int], keyword_setting: KeywordsSetting, **kwargs):
        super().__init__(
            title=t('settings.keywords.modal.title'),
            timeout=180,
            **kwargs
        )
        self.keyword_index = keyword_index
        self.setting = keyword_setting
        self.add_item(discore.ui.TextInput(
            label=t('settings.keywords.modal.value.label'),
            placeholder=t('settings.keywords.modal.value.placeholder'),
            custom_id='value',
            default=keyword_setting.keywords[keyword_index] if keyword_index is not None else None
        ))

    async def on_submit(self, interaction: discore.Interaction):
        children = self.children
        value_field = str(children[0])

        if len(value_field) > 50:
            await interaction.response.send_message(
                t('settings.keywords.modal.error.length', max=50), ephemeral=True, delete_after=10)
            return

        if value_field in self.setting.keywords and (
            self.keyword_index is None or
            value_field.index(value_field) != self.keyword_index
        ):
            await interaction.response.send_message(
                t('settings.keywords.modal.error.exists'), ephemeral=True, delete_after=10)
            return

        if self.keyword_index is not None:
            self.setting.keywords[self.keyword_index] = value_field
        else:
            self.setting.keywords.append(value_field)
            self.setting.selected_index = len(self.setting.keywords) - 1
        self.setting.ctx.guild.update({'keywords': self.setting.keywords})
        await self.setting.view.refresh(interaction)


class KeywordsSetting(BaseSetting):
    name = 'settings.keywords.name'
    id = 'keywords'
    description = 'settings.keywords.description'
    emoji = '🔤'

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            ctx: DataElements
    ):
        super().__init__(interaction, view, ctx)
        self.keywords = self.ctx.guild.keywords
        self.selected_index: Optional[int] = None
        self.use_allow_list = self.ctx.guild.keywords_use_allow_list

    @property
    async def embed(self) -> discore.Embed:
        keywords_str = "\n".join(
            [
                f'- **{keyword}**' if index == self.selected_index else f'- {keyword}'
                for index, keyword in enumerate(self.keywords)
            ] if self.keywords else ['*' + t('settings.keywords.empty') + '*']
        )
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                f'settings.keywords.content.{l(self.use_allow_list)}',
                keywords=keywords_str
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        # use the same structure as CustomWebsitesSetting
        if self.keywords:
            options = [
                discore.SelectOption(
                    label=keyword,
                    value=str(index),
                    default=index == self.selected_index
                )
                for index, keyword in enumerate(self.keywords)
                ]
        else:
            options = [discore.SelectOption(
                label=t('settings.keywords.empty'), value='0', default=True)]

        select = discore.ui.Select(
            placeholder=t('settings.keywords.button.placeholder'),
            options=options,
            custom_id='select_keyword',
            disabled=not self.keywords
        )
        edit_callback(select, self.view, self.select_keyword)
        if len(self.keywords) >= 3 and not is_premium(self.interaction):
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.keywords.button.premium'),
                custom_id='add_keyword',
                disabled=True
            )
        elif len(self.keywords) >= 25:
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.keywords.button.max'),
                custom_id='add_keyword',
                disabled=True
            )
        else:
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.keywords.button.add'),
                custom_id='add_keyword'
            )
            edit_callback(add_button, self.view, self.cu_keyword)
        edit_button = discore.ui.Button(
            label=t('settings.keywords.button.edit'),
            custom_id='edit_keyword',
            disabled=self.selected_index is None
        )
        edit_callback(edit_button, self.view, self.cu_keyword)
        delete_button = discore.ui.Button(
            style=discore.ButtonStyle.danger,
            label=t('settings.keywords.button.delete'),
            custom_id='delete_keyword',
            disabled=self.selected_index is None
        )
        edit_callback(delete_button, self.view, self.delete_keyword)
        if is_premium(self.interaction):
            toggle_mode_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.use_allow_list else discore.ButtonStyle.secondary,
                label=t(f'settings.keywords.button.toggle_mode.{l(self.use_allow_list)}'),
                custom_id=f'{self.id}_default'
            )
            edit_callback(toggle_mode_button, self.view, self.toggle_mode)
        else:
            toggle_mode_button = discore.ui.Button(
                label=t('settings.keywords.button.toggle_mode.premium'),
                disabled=True
            )

        return [select, add_button, edit_button, delete_button, toggle_mode_button]

    async def select_keyword(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        """
        Select a keyword from the dropdown
        :param view: The settings view
        :param interaction: The interaction
        :param select: The select component
        """
        self.selected_index = int(select.values[0])
        await view.refresh(interaction)

    async def cu_keyword(self, view: SettingsView, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        """
        Add or edit a keyword
        :param view: The settings view
        :param interaction: The interaction
        """
        await view.reset_timeout(interaction)
        await interaction.response.send_modal(KeywordModal(
            self.selected_index if button.custom_id == 'edit_keyword' else None,
            self
        ))

    async def delete_keyword(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        """
        Delete the selected keyword
        :param view: The settings view
        :param interaction: The interaction
        """
        del self.keywords[self.selected_index]
        self.ctx.guild.update({'keywords': self.keywords})
        self.selected_index = None
        await view.refresh(interaction)

    async def toggle_mode(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        """
        Toggle the keyword mode (allow or deny list)
        :param view: The settings view
        :param interaction: The interaction
        """
        if not is_premium(interaction):
            await view.refresh(interaction)
            return
        self.use_allow_list = not self.use_allow_list
        self.ctx.guild.update({'keywords_use_allow_list': self.use_allow_list})
        await view.refresh(interaction)


class OriginalMessageBehaviorSetting(BaseSetting):
    """
    Represents the original message behavior setting (delete, remove embeds or nothing)
    """

    name = 'settings.original_message.name'
    id = 'original_message'
    description = 'settings.original_message.description'
    emoji = '💬'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.state = ctx.guild.original_message

    @property
    async def embed(self) -> discore.Embed:
        option_tr_path = f'settings.original_message.option.{self.state.name.lower()}'
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.original_message.content',
                state=t(option_tr_path + '.emoji') + ' ' + t(option_tr_path + '.label'),
                channel=self.ctx.channel.mention,
                perms=format_perms(
                    ['manage_messages']
                    if self.state != OriginalMessage.NOTHING
                    else [],
                    self.ctx.channel.discord_object))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('⚠️ '
                   if self.state != OriginalMessage.NOTHING and is_missing_perm(['manage_messages'], self.ctx.channel.discord_object)
                   else '') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

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
        self.ctx.guild.update({'original_message': self.state.value}, cast=False)
        await view.refresh(interaction)


class ReplyMethodSetting(BaseSetting):
    """
    Represents the reply method setting (reply, or send)
    """

    name = 'settings.reply_method.name'
    id = 'reply_method'
    description = 'settings.reply_method.description'
    emoji = discore.config.emoji.reply

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.reply_to_message = bool(ctx.guild.reply_to_message)
        self.reply_silently = bool(ctx.guild.reply_silently)

    @property
    async def embed(self) -> discore.Embed:
        perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(self.ctx.channel.discord_object, discore.Thread):
            perms.append('send_messages_in_threads')
        if self.reply_to_message:
            perms.append('read_message_history')
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.reply_method.content',
                state=t(f'settings.reply_method.reply.state.{l(self.reply_to_message)}', emoji=self.emoji),
                silent=t(f'settings.reply_method.silent.state.{l(self.reply_silently)}'),
                perms=format_perms(perms, self.ctx.channel.discord_object))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('⚠️ ' if self.reply_to_message and is_missing_perm(['read_message_history'], self.ctx.channel.discord_object) else '')
                  + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def items(self) -> List[discore.ui.Item]:
        reply_to_message_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.reply_to_message else discore.ButtonStyle.secondary,
            label=t(f'settings.reply_method.reply.button.{l(self.reply_to_message)}'),
            custom_id=self.id
        )
        edit_callback(reply_to_message_button, self.view, self.toggle_reply_to_message)
        reply_silently_button = discore.ui.Button(
            style=discore.ButtonStyle.secondary if self.reply_silently else discore.ButtonStyle.primary,
            label=t(f'settings.reply_method.silent.button.{l(self.reply_silently)}'),
            custom_id='reply_silently'
        )
        edit_callback(reply_silently_button, self.view, self.toggle_reply_silently)
        return [reply_to_message_button, reply_silently_button]

    async def toggle_reply_to_message(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_to_message = not self.reply_to_message
        self.ctx.guild.update({'reply_to_message': self.reply_to_message})
        await view.refresh(interaction)

    async def toggle_reply_silently(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_silently = not self.reply_silently
        self.ctx.guild.update({'reply_silently': self.reply_silently})
        await view.refresh(interaction)


class WebhooksSetting(BaseSetting):
    """
    Represents the
    """

    name = 'settings.webhooks.name'
    id = 'webhooks'
    description = 'settings.webhooks.description'
    emoji = discore.config.emoji.webhooks

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.state = bool(ctx.guild.db_object.webhooks)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.webhooks.content',
                state=t(f'settings.webhooks.state.{l(self.state)}'))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.webhooks.button.{l(self.state)}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.ctx.guild.update({'webhooks': self.state})
        await view.refresh(interaction)


class TwitterSetting(WebsiteBaseSetting):
    """
    Represents the twitter setting
    """

    id = 'twitter'
    name = 'Twitter'
    emoji = discore.config.emoji.twitter
    proxies = {"FxTwitter": "https://github.com/FxEmbed/FxEmbed"}
    is_translation = True
    is_view = True


class InstagramSetting(WebsiteBaseSetting):
    """
    Represents the instagram setting
    """

    id = 'instagram'
    name = 'Instagram'
    emoji = discore.config.emoji.instagram
    proxies = {"InstaFix": "https://github.com/gigirassy/InstaFix"}


class TikTokSetting(WebsiteBaseSetting):
    """
    Represents the tiktok setting
    """

    id = 'tiktok'
    name = 'TikTok'
    emoji = discore.config.emoji.tiktok
    proxies = {"fxTikTok": "https://github.com/okdargy/fxTikTok"}
    is_view = True


class RedditSetting(WebsiteBaseSetting):
    """
    Represents the reddit setting
    """

    id = 'reddit'
    name = 'Reddit'
    emoji = discore.config.emoji.reddit
    proxies = {"vxreddit": "https://github.com/dylanpdx/vxReddit"}


class ThreadsSetting(WebsiteBaseSetting):
    """
    Represents the threads setting
    """

    id = 'threads'
    name = 'Threads'
    emoji = discore.config.emoji.threads
    proxies = {"FixThreads": "https://github.com/milanmdev/fixthreads"}


class BlueskySetting(WebsiteBaseSetting):
    """
    Represents the bluesky setting
    """

    id = 'bluesky'
    name = 'Bluesky'
    emoji = discore.config.emoji.bluesky
    proxies = {"VixBluesky": "https://github.com/Lexedia/VixBluesky"}
    is_view = True


class SnapchatSetting(EmbedEZBaseSetting):
    """
    Represents the snapchat setting
    """

    id = 'snapchat'
    name = 'Snapchat'
    emoji = discore.config.emoji.snapchat


class FacebookSetting(WebsiteBaseSetting):
    """
    Represents the facebook setting
    """

    id = 'facebook'
    name = 'Facebook'
    emoji = discore.config.emoji.facebook
    proxies = {"facebed": "https://github.com/4pii4/facebed"}


class PixivSetting(WebsiteBaseSetting):
    """
    Represents the pixiv setting
    """

    id = 'pixiv'
    name = 'Pixiv'
    emoji = discore.config.emoji.pixiv
    proxies = {"phixiv": "https://github.com/thelaao/phixiv"}


class TwitchSetting(WebsiteBaseSetting):
    """
    Represents the twitch setting
    """

    id = 'twitch'
    name = 'Twitch'
    emoji = discore.config.emoji.twitch
    proxies = {"fxtwitch": "https://github.com/seriaati/fxtwitch"}


class SpotifySetting(WebsiteBaseSetting):
    """
    Represents the spotify setting
    """

    id = 'spotify'
    name = 'Spotify'
    emoji = discore.config.emoji.spotify
    proxies = {"fxspotify": "https://github.com/dotconnexion/fxspotify"}


class DeviantArtSetting(WebsiteBaseSetting):
    """
    Represents the deviantart setting
    """

    id = 'deviantart'
    name = 'DeviantArt'
    emoji = discore.config.emoji.deviantart
    proxies = {"fixDeviantArt": "https://github.com/Tschrock/fixdeviantart"}


class MastodonSetting(WebsiteBaseSetting):
    """
    Represents the mastodon setting
    """

    id = 'mastodon'
    name = 'Mastodon'
    emoji = discore.config.emoji.mastodon
    proxies = {"FxMastodon": "https://fx.zillanlabs.tech/"}


class TumblrSetting(WebsiteBaseSetting):
    """
    Represents the tumblr setting
    """

    id = 'tumblr'
    name = 'Tumblr'
    emoji = discore.config.emoji.tumblr
    proxies = {"fxtumblr": "https://github.com/knuxify/fxtumblr"}


class BilibiliSetting(WebsiteBaseSetting):
    """
    Represents the bilibili setting
    """

    id = 'bilibili'
    name = 'BiliBili'
    emoji = discore.config.emoji.bilibili
    proxies = {"BiliFix": "https://www.vxbilibili.com/"}


class IFunnySetting(EmbedEZBaseSetting):
    """
    Represents the ifunny setting
    """

    id = 'ifunny'
    name = 'iFunny'
    emoji = discore.config.emoji.ifunny


class FurAffinitySetting(WebsiteBaseSetting):
    """
    Represents the furaffinity setting
    """

    id = 'furaffinity'
    name = 'Fur Affinity'
    emoji = discore.config.emoji.furaffinity
    proxies = {"xfuraffinity": "https://github.com/FirraWoof/xfuraffinity"}


class YouTubeSetting(WebsiteBaseSetting):
    """
    Represents the youtube setting
    """

    id = 'youtube'
    name = 'YouTube'
    emoji = discore.config.emoji.youtube
    proxies = {"Koutube": "https://github.com/iGerman00/koutube"}


class ImgurSetting(EmbedEZBaseSetting):
    """
    Represents the Imgur setting
    """

    id = 'imgur'
    name = 'Imgur'
    emoji = discore.config.emoji.imgur


class WeiboSetting(EmbedEZBaseSetting):
    """
    Represents the Weibo setting
    """

    id = 'weibo'
    name = 'Weibo'
    emoji = discore.config.emoji.weibo


class ImageboardsSetting(EmbedEZBaseSetting):
    """
    Represents the multiple imageboards setting
    """

    id = 'imageboards'
    emoji = discore.config.emoji.imageboards
    is_translation = False

    @property
    def name(self):
        return t('settings.imageboards')


class PinterestSetting(EmbedEZBaseSetting):
    """
    Represents the Pinterest setting
    """

    id = 'pinterest'
    name = 'Pinterest'
    emoji = discore.config.emoji.pinterest


class CustomWebsiteModal(discore.ui.Modal):

    def __init__(self, website: Optional[CustomWebsite], website_setting: CustomWebsitesSetting, **kwargs):
        super().__init__(
            title=t('settings.custom_websites.modal.title'),
            timeout=180,
            **kwargs
        )
        self.website = website
        self.setting = website_setting
        self.add_item(discore.ui.TextInput(
            label=t('settings.custom_websites.modal.name.label'),
            placeholder=t('settings.custom_websites.modal.name.placeholder'),
            custom_id='name',
            default=website.name if website else None
        ))
        self.add_item(discore.ui.TextInput(
            label=t('settings.custom_websites.modal.domain.label'),
            placeholder=t('settings.custom_websites.modal.domain.placeholder'),
            custom_id='domain',
            default=website.domain if website else None
        ))
        self.add_item(discore.ui.TextInput(
            label=t('settings.custom_websites.modal.fix_domain.label'),
            placeholder=t('settings.custom_websites.modal.fix_domain.placeholder'),
            custom_id='fix_domain',
            default=website.fix_domain if website else None
        ))

    async def on_submit(self, interaction: discore.Interaction):
        children = self.children
        name_field = str(children[0])
        domain_field = str(children[1])
        fix_domain_field = str(children[2])

        if domain_field.startswith('http://') or domain_field.startswith('https://'):
            domain_field = domain_field.split('://', 1)[1]
        if domain_field.startswith('www.'):
            domain_field = domain_field[4:]
        if domain_field.endswith('/'):
            domain_field = domain_field[:-1]
        if fix_domain_field.startswith('http://') or fix_domain_field.startswith('https://'):
            fix_domain_field = fix_domain_field.split('://', 1)[1]
        if fix_domain_field.startswith('www.'):
            fix_domain_field = fix_domain_field[4:]
        if fix_domain_field.endswith('/'):
            fix_domain_field = fix_domain_field[:-1]

        if not domain_field or not fix_domain_field:
            await interaction.response.send_message(
                t('settings.custom_websites.modal.error.length'), ephemeral=True, delete_after=10)
            return

        custom_website = CustomWebsite.where('guild_id', interaction.guild.id).where({
            'guild_id': interaction.guild.id,
            'domain': domain_field
        }).first()
        if custom_website and (not self.website or custom_website.id != self.website.id):
            await interaction.response.send_message(
                t('settings.custom_websites.modal.error.exists'), ephemeral=True, delete_after=10)
            return

        if len(name_field) > 36:
            await interaction.response.send_message(
                t('settings.custom_websites.modal.error.length_name', max=36), ephemeral=True, delete_after=10)
            return

        if len(domain_field) > 61:
            await interaction.response.send_message(
                t('settings.custom_websites.modal.error.length_domain', max=61), ephemeral=True, delete_after=10)
            return

        if self.website:
            old_website = self.website
            self.website.update({
                'name': name_field,
                'domain': domain_field,
                'fix_domain': fix_domain_field
            })
            self.setting.custom_websites._items.remove(old_website)
        else:
            self.website = CustomWebsite.create(
                guild_id=interaction.guild.id,
                name=name_field,
                domain=domain_field,
                fix_domain=fix_domain_field
            )
        self.setting.custom_websites._items.append(self.website)
        self.setting.selected = self.website
        await self.setting.view.refresh(interaction)


class CustomWebsitesSetting(BaseSetting):
    """
    Represents the custom websites setting
    """

    name = 'settings.custom_websites.name'
    id = 'custom_websites'
    description = 'settings.custom_websites.description'
    emoji = '🌐'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.custom_websites = ctx.guild.custom_websites[:25]
        self.selected: Optional[CustomWebsite] = None

    @property
    async def embed(self) -> discore.Embed:
        website_list = (
            '\n'.join([
                t(
                    'settings.custom_websites.selected_website'
                    if website == self.selected else 'settings.custom_websites.website',
                    name=website.name,
                    domain=website.domain,
                    fix_domain=website.fix_domain)
                for website in self.custom_websites
            ])
        )
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=(
                t('settings.custom_websites.content')
                + ((t('settings.custom_websites.list') + website_list) if website_list else '')
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        if self.custom_websites:
            options = [
                discore.SelectOption(
                    label=f"{website.name} ({website.domain})",
                    value=website.domain,
                    default=website == self.selected
                )
                for website in self.custom_websites
            ]
        else:
            options = [discore.SelectOption(
                label=t('settings.custom_websites.empty'), default=True)]

        selector = discore.ui.Select(
            options=options,
            placeholder=t('settings.custom_websites.placeholder'),
            disabled=not self.custom_websites
        )
        edit_callback(selector, self.view, self.select_action)
        if len(self.custom_websites) >= 3 and not is_premium(self.interaction):
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.custom_websites.button.premium'),
                custom_id='add_website',
                disabled=True
            )
        elif len(self.custom_websites) >= 25:
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.custom_websites.button.max'),
                custom_id='add_website',
                disabled=True
            )
        else:
            add_button = discore.ui.Button(
                style=discore.ButtonStyle.primary,
                label=t('settings.custom_websites.button.add'),
                custom_id='add_website'
            )
            edit_callback(add_button, self.view, self.action)
        edit_button = discore.ui.Button(
            label=t('settings.custom_websites.button.edit'),
            custom_id='edit_website',
            disabled=not self.selected
        )
        edit_callback(edit_button, self.view, self.action)
        delete_button = discore.ui.Button(
            style=discore.ButtonStyle.danger,
            label=t('settings.custom_websites.button.delete'),
            custom_id='delete_website',
            disabled=not self.selected
        )
        edit_callback(delete_button, self.view, self.delete_action)
        return [selector, add_button, edit_button, delete_button]

    async def action(self, _, interaction: discore.Interaction, button: discore.ui.Button) -> None:
        await self.view.reset_timeout(interaction)
        await interaction.response.send_modal(CustomWebsiteModal(
            self.selected if button.custom_id == 'edit_website' else None,
            self
        ))

    async def delete_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.selected.delete()
        self.custom_websites._items.remove(self.selected)
        self.selected = None
        await view.refresh(interaction)

    async def select_action(self, view: SettingsView, interaction: discore.Interaction,
                            select: discore.ui.Select) -> None:
        self.selected = next((
            website for website in self.custom_websites
            if website.domain == select.values[0]), None)
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.custom_websites else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )


class WebsiteSettings(BaseSetting):
    """
    Represents the settings website category
    """
    name = 'settings.websites.name'
    id = 'websites'
    description = 'settings.websites.description'
    emoji = '🌐'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            CustomWebsitesSetting(interaction, view, ctx),
            TwitterSetting(interaction, view, ctx),
            InstagramSetting(interaction, view, ctx),
            TikTokSetting(interaction, view, ctx),
            RedditSetting(interaction, view, ctx),
            ThreadsSetting(interaction, view, ctx),
            BlueskySetting(interaction, view, ctx),
            SnapchatSetting(interaction, view, ctx),
            FacebookSetting(interaction, view, ctx),
            PinterestSetting(interaction, view, ctx),
            PixivSetting(interaction, view, ctx),
            TwitchSetting(interaction, view, ctx),
            SpotifySetting(interaction, view, ctx),
            DeviantArtSetting(interaction, view, ctx),
            MastodonSetting(interaction, view, ctx),
            TumblrSetting(interaction, view, ctx),
            BilibiliSetting(interaction, view, ctx),
            WeiboSetting(interaction, view, ctx),
            ImgurSetting(interaction, view, ctx),
            IFunnySetting(interaction, view, ctx),
            YouTubeSetting(interaction, view, ctx),
            FurAffinitySetting(interaction, view, ctx),
            ImageboardsSetting(interaction, view, ctx)
        ))
        self.selected_id: Optional[str] = None

    @property
    async def embed(self) -> discore.Embed:
        if self.selected_id is not None:
            return await self.settings[self.selected_id].embed

        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t('settings.websites.content')
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        selected_items = await self.settings[self.selected_id].items if self.selected_id else []
        options = []
        for setting_id in self.settings:
            option = await self.settings[setting_id].option
            if setting_id == self.selected_id:
                option.default = True
            options.append(option)

        parameter_selection = discore.ui.Select(options=options, row=3, placeholder=t('settings.websites.placeholder'))
        edit_callback(parameter_selection, self.view, self.action)

        return selected_items + [parameter_selection]

    async def action(self, _, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.selected_id = select.values[0]
        await self.view.refresh(interaction)


class SettingsView(discore.ui.View):

    def __init__(self, i: discore.Interaction):
        super().__init__()

        self.bot: discore.Bot = i.client
        self.ctx = DataElements(i)
        self.embed: Optional[discore.Embed] = None
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            TroubleshootingSetting(i, self, self.ctx),
            ChannelSetting(i, self, self.ctx),
            MemberSetting(i, self, self.ctx),
            RoleSetting(i, self, self.ctx),
            KeywordsSetting(i, self, self.ctx),
            WebsiteSettings(i, self, self.ctx),
            OriginalMessageBehaviorSetting(i, self, self.ctx),
            ReplyMethodSetting(i, self, self.ctx),
            WebhooksSetting(i, self, self.ctx),
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

        parameter_selection = discore.ui.Select(options=options, row=4, placeholder=t('settings.placeholder'))
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

    async def reset_timeout(self, interaction: discore.Interaction) -> None:
        """
        Reset the timeout task
        :return: None
        """
        if self.timeout_task is not None:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self._message_delete_after(interaction))

    async def refresh(self, interaction: discore.Interaction) -> None:
        """
        Send or refresh the built view (if already sent) with the current settings
        :param interaction: The interaction to respond to
        :return: None
        """
        await self.build()

        # Discord API sometimes returns incorrect error code, in this case 404 Unknown interaction when interaction
        # is actually found and the message has been sent.
        # Even if the interaction is really not found, there's not much we can do (as the interaction is lost),
        # so in both cases we just ignore the error.
        try:
            if interaction.message is not None:
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(
                    view=self, embed=self.embed)
            else:
                # noinspection PyUnresolvedReferences
                await interaction.response.send_message(
                    view=self, embed=self.embed, ephemeral=True)
        except discore.NotFound:
            pass

        await self.reset_timeout(interaction)

    send = refresh
