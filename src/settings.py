"""
Settings view for the bot
"""

from __future__ import annotations
import asyncio
from typing import Type, List, overload, Iterable, Any

import discore.ui.select

from database.models.Role import Role
from database.models.TextChannel import *
from database.models.Guild import *
from database.models.Member import *
from database.models.CustomWebsite import CustomWebsite

from src.utils import *

__all__ = ('SettingsView',)


class DataElements:
    """Represents the database elements for the settings view"""

    def __init__(self, interaction: discore.Interaction):
        self.guild = HybridElement(interaction.guild, Guild)
        self.member = HybridElement(interaction.user, Member, guild=self.guild)
        self.channel = HybridElement(interaction.channel, TextChannel, guild=self.guild)
        self.role = HybridElement(interaction.user.top_role, Role, guild=self.guild)
        self.roles = [HybridElement(role, Role, guild=self.guild) for role in interaction.user.roles]

    def refresh(self):
        """Refresh the data elements"""

        self.guild.db_object = self.guild.db_object.fresh()
        self.member.db_object = self.member.db_object.fresh()
        self.channel.db_object = self.channel.db_object.fresh()
        self.role.db_object = self.role.db_object.fresh()
        self.roles.clear()
        self.roles.extend(
            HybridElement(role, Role, guild=self.guild) for role in self.member.discord_object.roles
        )


class BaseSetting:
    """Represents a bot setting"""

    name: str
    id: str
    description: str
    emoji: str | None

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        self.interaction: discore.Interaction = interaction
        self.bot: discore.Client = interaction.client
        self.view: SettingsView = view
        self.ctx: DataElements = ctx

    @property
    def title(self) -> str:
        """
        Build the setting title
        :return: The title
        """
        return f"{self.emoji} {t(self.name)}" if self.emoji else t(self.name)

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
    async def layout(self) -> List[discore.ui.Item]:
        """
        Build the setting components (its texts and controls), displayed below its title
        :return: The components
        """
        return [discore.ui.TextDisplay(t(self.description))]

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
    """Represents the website base setting"""

    proxies: dict[str, str]
    is_view: bool = False
    is_translation: bool = False
    view_enum: Type[GettableEnum] | None = None

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            ctx: DataElements
    ):
        super().__init__(interaction, view, ctx)
        self.state = bool(self.ctx.guild[self.id])
        self.view_state = None
        self.translation = None
        if self.is_view:
            self.view_state = self.ctx.guild[f'{self.id}_view']
            if self.view_enum is None:
                enum_name = f'{self.id.title()}View'
                self.view_enum = getattr(__import__('database.models.Guild', fromlist=[enum_name]), enum_name)
        if self.is_translation:
            self.translation = bool(self.ctx.guild[f'{self.id}_tr'])
            self.lang = self.ctx.guild.lang

    @property
    def title(self) -> str:
        return f"{self.emoji} {self.name}"

    @property
    async def layout(self) -> List[discore.ui.Item]:
        self.lang = self.ctx.guild.lang if self.is_translation else None
        state_switch = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.base_website.button.state.{l(self.state)}'),
            custom_id=self.id
        )
        edit_callback(state_switch, self.view, self.action)
        items = [discore.ui.Section(
            t(
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
            ),
            accessory=state_switch
        )]
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
            translation_lang_button = discore.ui.Button(
                label=t('settings.base_website.button.translation_lang'),
                custom_id=f'{self.id}_translation_lang',
                disabled=not (self.translation and self.state)
            )
            edit_callback(translation_lang_button, self.view, self.translation_lang_action)
            items.append(discore.ui.ActionRow(translation_button, translation_lang_button))
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
            items.append(discore.ui.ActionRow(view_selector))

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


class Modal(discore.ui.Modal):
    """A modal displayed in the language of the user submitting it"""

    async def interaction_check(self, interaction: discore.Interaction) -> bool:
        # The texts are built from the global locale, which is otherwise only set when a command is invoked
        discore.set_locale(interaction)
        return True


class TranslationModal(Modal):
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
        self.interaction_lang = setting.interaction.locale.value.split('-')[0]
        # noinspection PyUnresolvedReferences
        self.lang = discore.ui.TextInput(
            placeholder=t('settings.lang_modal.placeholder', lang_iso=self.interaction_lang),
            custom_id='lang',
            default=setting.ctx.guild.lang
        )
        self.add_item(discore.ui.Label(text=t('settings.lang_modal.label'), component=self.lang))

    async def on_submit(self, interaction: discore.Interaction):
        lang = self.lang.value.strip().lower()
        if len(lang) != 2 or not (lang.isascii() and lang.isalpha()):
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                view=notice(t('settings.lang_modal.error', invalid_lang=lang, lang_iso=self.interaction_lang)), ephemeral=True, delete_after=10)
            return
        self.setting.ctx.guild.update({'lang': lang})
        await self.setting.view.refresh(interaction)


class EmbedEZBaseSetting(WebsiteBaseSetting):
    """Represents the EmbedEZ base setting"""

    proxies = {"EmbedEZ": "https://embedez.com"}
    is_view = True
    is_translation = True
    view_enum = EmbedEzView


class TroubleshootingSetting(BaseSetting):
    """Represents the troubleshooting setting"""

    name = 'settings.troubleshooting.name'
    id = 'troubleshooting'
    description = 'settings.troubleshooting.description'
    emoji = '🛠️'

    @property
    async def layout(self) -> List[discore.ui.Item]:
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
        if self.ctx.guild.reply_as_original_author_replica:
            perms.append('manage_webhooks')
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
        # (name, value)
        fields = [
            (t('settings.troubleshooting.ping.name'),
             t('settings.troubleshooting.ping.value', latency=format(self.bot.latency * 1000, '.0f'))),
            (t('settings.troubleshooting.permissions', channel=self.ctx.channel.mention),
             format_perms(perms, self.ctx.channel.discord_object, include_label=False, include_valid=True)),
            (t('settings.troubleshooting.filters'), "\n".join(
                ('  - ' if indented else '- ') + t(f'settings.{id}.state.{l(state)}',
                                                   **{'element': display_value, 'details': ''})
                for id, display_value, state, indented in options)),
            (t('settings.troubleshooting.websites'), "\n".join(
                '- ' + t(
                    f'settings.base_website.state.{l(bool(self.ctx.guild[website.id]))}',
                    name=website.name, translation='')
                for website in self.view.settings['websites'].settings.values()
                if isinstance(website, WebsiteBaseSetting))),
        ]
        if custom_websites := self.ctx.guild.custom_websites:
            fields.append((t('settings.troubleshooting.custom_websites'), "\n".join(
                f"- `{website.domain}`" for website in custom_websites)))
        fields.append((
            t('settings.troubleshooting.premium.name'),
            t(f'settings.troubleshooting.premium.{l(bool(is_premium(self.interaction)))}')))

        refresh_button = discore.ui.Button(
            label=t('settings.troubleshooting.refresh')
        )
        edit_callback(refresh_button, self.view, self.refresh_action)
        buttons = discore.ui.ActionRow(refresh_button)
        if not is_premium(self.interaction) and is_sku():
            buttons.add_item(discore.ui.Button(
                style=discore.ButtonStyle.premium,
                sku_id=discore.config.sku
            ))
        buttons.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.support'),
            url=discore.config.support_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.discord)
        ))
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
        return [
            discore.ui.TextDisplay(t(self.description)),
            *(discore.ui.TextDisplay(f"### {name}\n{value}") for name, value in fields),
            buttons,
            discore.ui.ActionRow(select_channel),
            discore.ui.ActionRow(select_member),
        ]

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
    """Represents a generic filter setting"""

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

    def toggle_button(self) -> discore.ui.Button:
        """
        Build the button enabling or disabling the selected element
        :return: The button
        """
        return discore.ui.Button(
            style=discore.ButtonStyle.primary if self.enabled else discore.ButtonStyle.secondary,
            label=t(f'settings.filters.button.toggle.{l(self.enabled)}'),
            custom_id=f'{self.id}_toggle'
        )

    @property
    async def layout(self) -> List[discore.ui.Item]:
        toggle_button = edit_callback(self.toggle_button(), self.view, self.toggle)
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
        self.reset_clicked_level -= 1
        selector = self.Select(
            custom_id=f'{self.id}_select',
            default_values=[self.element.discord_object],
            placeholder=t(f'settings.{self.id}.select'),
            **self.select_kwargs
        )
        edit_callback(selector, self.view, self.select_element)
        items = [
            discore.ui.TextDisplay(f"**{t(self.description)}**"),
            discore.ui.Section(
                t(f'settings.{self.id}.state.{l(self.enabled)}',
                  element=self.element.mention,
                  details=t(f'settings.filters.labels.details.on_list.{l(self.element.on_list(self.ctx.guild))}',
                            list=t(f'settings.filters.labels.details.list.{l(self.use_deny_list)}'))),
                accessory=toggle_button),
            discore.ui.Section(
                t(f'settings.filters.labels.default.{l(self.use_deny_list)}'),
                accessory=toggle_default_button),
            *self.extra_sections(),
        ]
        if missing_perms := format_perms(self.perms, self.ctx.channel.discord_object).strip():
            items.append(discore.ui.TextDisplay(missing_perms))
        return items + [discore.ui.ActionRow(selector), discore.ui.ActionRow(reset_button)]

    def extra_sections(self) -> List[discore.ui.Item]:
        """
        Build the sections specific to the setting, displayed below the common ones
        :return: The sections
        """
        return []

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
    """Represents the member setting"""

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

    def toggle_button(self) -> discore.ui.Button:
        if is_premium(self.interaction) or not self.ctx.member.bot:
            return super().toggle_button()
        return discore.ui.Button(
            label=t('settings.members.toggle_bot_premium'),
            disabled=True
        )


class ChannelSetting(GenericFilterSetting):
    """Represents the channel setting"""

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

    def extra_sections(self) -> List[discore.ui.Item]:
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
        return [discore.ui.Section(
            t(f'settings.{self.id}.rule.{l(self.use_any_rule)}'),
            accessory=toggle_rule_button)]

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


class KeywordModal(Modal):

    def __init__(self, keyword_index: int | None, keyword_setting: KeywordsSetting, **kwargs):
        super().__init__(
            title=t('settings.keywords.modal.title'),
            timeout=180,
            **kwargs
        )
        self.keyword_index = keyword_index
        self.setting = keyword_setting
        self.keyword = discore.ui.TextInput(
            placeholder=t('settings.keywords.modal.value.placeholder'),
            custom_id='value',
            default=keyword_setting.keywords[keyword_index] if keyword_index is not None else None
        )
        self.add_item(discore.ui.Label(text=t('settings.keywords.modal.value.label'), component=self.keyword))

    async def on_submit(self, interaction: discore.Interaction):
        value_field = self.keyword.value.strip()

        if not value_field:
            # A keyword made of spaces can't be listed, and would match nearly every message
            await self.setting.view.refresh(interaction)
            return

        if len(value_field) > 50:
            await interaction.response.send_message(
                view=notice(t('settings.keywords.modal.error.length', max=50)), ephemeral=True, delete_after=10)
            return

        if value_field in self.setting.keywords and (
            self.keyword_index is None or
            self.setting.keywords.index(value_field) != self.keyword_index
        ):
            await interaction.response.send_message(
                view=notice(t('settings.keywords.modal.error.exists')), ephemeral=True, delete_after=10)
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
        self.selected_index: int | None = None
        self.use_allow_list = self.ctx.guild.keywords_use_allow_list

    @property
    async def layout(self) -> List[discore.ui.Item]:
        keywords_str = "\n".join(
            [
                f'- **{keyword}**' if index == self.selected_index else f'- {keyword}'
                for index, keyword in enumerate(self.keywords)
            ] if self.keywords else ['*' + t('settings.keywords.empty') + '*']
        )
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
        items = [discore.ui.Section(
            t(f'settings.keywords.content.{l(self.use_allow_list)}', keywords=keywords_str),
            accessory=toggle_mode_button
        )]

        if self.keywords:
            select = discore.ui.Select(
                placeholder=t('settings.keywords.button.placeholder'),
                options=[
                    discore.SelectOption(
                        label=keyword,
                        value=str(index),
                        default=index == self.selected_index
                    )
                    for index, keyword in enumerate(self.keywords)
                ],
                custom_id='select_keyword'
            )
            edit_callback(select, self.view, self.select_keyword)
            items.append(discore.ui.ActionRow(select))

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
        items.append(discore.ui.ActionRow(add_button, edit_button, delete_button))
        return items

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
        :param button: The button
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
    """Represents the original message behavior setting (delete, remove embeds or nothing)"""

    name = 'settings.original_message.name'
    id = 'original_message'
    description = 'settings.original_message.description'
    emoji = '💬'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.state = ctx.guild.original_message

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
    async def layout(self) -> List[discore.ui.Item]:
        option_tr_path = f'settings.original_message.option.{self.state.name.lower()}'
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
        return [
            discore.ui.TextDisplay(t(
                'settings.original_message.content',
                state=t(option_tr_path + '.emoji') + ' ' + t(option_tr_path + '.label'),
                channel=self.ctx.channel.mention,
                perms=format_perms(
                    ['manage_messages']
                    if self.state != OriginalMessage.NOTHING
                    else [],
                    self.ctx.channel.discord_object))),
            discore.ui.ActionRow(item)
        ]

    async def action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.state = OriginalMessage[select.values[0]]
        self.ctx.guild.update({'original_message': self.state.value}, cast=False)
        await view.refresh(interaction)


class ReplyMethodSetting(BaseSetting):
    """Represents the reply method setting (reply, or send)"""

    name = 'settings.reply_method.name'
    id = 'reply_method'
    description = 'settings.reply_method.description'
    emoji = discore.config.emoji.reply

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.reply_as_original_author_replica = bool(ctx.guild.reply_as_original_author_replica)
        self.reply_to_message = bool(ctx.guild.reply_to_message and not self.reply_as_original_author_replica)
        self.reply_silently = bool(ctx.guild.reply_silently)

    @property
    async def option(self) -> discore.SelectOption:
        has_missing_perms = (
            (self.reply_to_message and is_missing_perm(['read_message_history'], self.ctx.channel.discord_object))
            or (self.reply_as_original_author_replica
                and is_missing_perm(['manage_webhooks'], self.ctx.channel.discord_object))
        )
        return discore.SelectOption(
            label=('⚠️ ' if has_missing_perms else '')
                  + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def layout(self) -> List[discore.ui.Item]:
        perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(self.ctx.channel.discord_object, discore.Thread):
            perms.append('send_messages_in_threads')
        if self.reply_to_message:
            perms.append('read_message_history')
        if self.reply_as_original_author_replica:
            perms.append('manage_webhooks')
        reply_to_message_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.reply_to_message else discore.ButtonStyle.secondary,
            label=t(f'settings.reply_method.reply.button.{l(self.reply_to_message)}'),
            custom_id=self.id,
            disabled=self.reply_as_original_author_replica
        )
        edit_callback(reply_to_message_button, self.view, self.toggle_reply_to_message)
        reply_silently_button = discore.ui.Button(
            style=discore.ButtonStyle.secondary if self.reply_silently else discore.ButtonStyle.primary,
            label=t(f'settings.reply_method.silent.button.{l(self.reply_silently)}'),
            custom_id='reply_silently'
        )
        edit_callback(reply_silently_button, self.view, self.toggle_reply_silently)
        original_author_replica_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.reply_as_original_author_replica else discore.ButtonStyle.secondary,
            label=t(
                f'settings.reply_method.original_author_replica.button.{l(self.reply_as_original_author_replica)}',
                bot=self.bot.user.display_name),
            custom_id='reply_as_original_author_replica'
        )
        edit_callback(original_author_replica_button, self.view, self.toggle_reply_as_original_author_replica)
        items = [
            discore.ui.TextDisplay(f"**{t(self.description)}**"),
            discore.ui.Section(
                t(f'settings.reply_method.reply.state.{l(self.reply_to_message)}', emoji=self.emoji),
                accessory=reply_to_message_button),
            discore.ui.Section(
                t(f'settings.reply_method.silent.state.{l(self.reply_silently)}'),
                accessory=reply_silently_button),
            discore.ui.Section(
                t(f'settings.reply_method.original_author_replica.state.{l(self.reply_as_original_author_replica)}',
                  bot=self.bot.user.display_name),
                accessory=original_author_replica_button),
        ]
        if missing_perms := format_perms(perms, self.ctx.channel.discord_object).strip():
            items.append(discore.ui.TextDisplay(missing_perms))
        return items

    async def toggle_reply_to_message(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if self.reply_as_original_author_replica:
            return
        self.reply_to_message = not self.reply_to_message
        self.ctx.guild.update({'reply_to_message': self.reply_to_message})
        await view.refresh(interaction)

    async def toggle_reply_silently(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_silently = not self.reply_silently
        self.ctx.guild.update({'reply_silently': self.reply_silently})
        await view.refresh(interaction)

    async def toggle_reply_as_original_author_replica(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_as_original_author_replica = not self.reply_as_original_author_replica
        if self.reply_as_original_author_replica:
            self.reply_to_message = False
        self.ctx.guild.update({
            'reply_as_original_author_replica': self.reply_as_original_author_replica,
            'reply_to_message': self.reply_to_message
        })
        await view.refresh(interaction)


class WebhooksSetting(BaseSetting):
    """Represents the webhooks setting (respond to webhooks or not)"""

    name = 'settings.webhooks.name'
    id = 'webhooks'
    description = 'settings.webhooks.description'
    emoji = discore.config.emoji.webhooks

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.state = bool(ctx.guild.db_object.webhooks)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def layout(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.webhooks.button.{l(self.state)}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [discore.ui.Section(
            t('settings.webhooks.content', state=t(f'settings.webhooks.state.{l(self.state)}')),
            accessory=item
        )]

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.ctx.guild.update({'webhooks': self.state})
        await view.refresh(interaction)


class TwitterSetting(WebsiteBaseSetting):
    """Represents the twitter setting"""

    id = 'twitter'
    name = 'Twitter'
    emoji = discore.config.emoji.twitter
    proxies = {"FxTwitter": "https://github.com/FxEmbed/FxEmbed"}
    is_translation = True
    is_view = True
    view_enum = FxEmbedView


class InstagramSetting(WebsiteBaseSetting):
    """Represents the instagram setting"""

    id = 'instagram'
    name = 'Instagram'
    emoji = discore.config.emoji.instagram
    proxies = {"OGInstagram": "https://github.com/seirenkr/OGInstagram"}
    is_view = True


class TikTokSetting(WebsiteBaseSetting):
    """Represents the tiktok setting"""

    id = 'tiktok'
    name = 'TikTok'
    emoji = discore.config.emoji.tiktok
    proxies = {"fxTikTok": "https://github.com/okdargy/fxTikTok"}
    is_view = True


class RedditSetting(WebsiteBaseSetting):
    """Represents the reddit setting"""

    id = 'reddit'
    name = 'Reddit'
    emoji = discore.config.emoji.reddit
    proxies = {"vxreddit": "https://github.com/dylanpdx/vxReddit"}


class ThreadsSetting(WebsiteBaseSetting):
    """Represents the threads setting"""

    id = 'threads'
    name = 'Threads'
    emoji = discore.config.emoji.threads
    proxies = {"FixThreads": "https://github.com/seriaati/fixthreads"}


class BlueskySetting(WebsiteBaseSetting):
    """Represents the bluesky setting"""

    id = 'bluesky'
    name = 'Bluesky'
    emoji = discore.config.emoji.bluesky
    proxies = {"FxBluesky": "https://github.com/FxEmbed/FxEmbed"}
    is_view = True
    view_enum = FxEmbedView


class SnapchatSetting(EmbedEZBaseSetting):
    """Represents the snapchat setting"""

    id = 'snapchat'
    name = 'Snapchat'
    emoji = discore.config.emoji.snapchat


class FacebookSetting(WebsiteBaseSetting):
    """Represents the facebook setting"""

    id = 'facebook'
    name = 'Facebook'
    emoji = discore.config.emoji.facebook
    proxies = {"facebed": "https://github.com/seriaati/facebed"}


class PixivSetting(WebsiteBaseSetting):
    """Represents the pixiv setting"""

    id = 'pixiv'
    name = 'Pixiv'
    emoji = discore.config.emoji.pixiv
    proxies = {"phixiv": "https://github.com/thelaao/phixiv"}


class TwitchSetting(WebsiteBaseSetting):
    """Represents the twitch setting"""

    id = 'twitch'
    name = 'Twitch'
    emoji = discore.config.emoji.twitch
    proxies = {"fxtwitch": "https://github.com/seriaati/fxtwitch"}


class SpotifySetting(WebsiteBaseSetting):
    """Represents the spotify setting"""

    id = 'spotify'
    name = 'Spotify'
    emoji = discore.config.emoji.spotify
    proxies = {"fxspotify": "https://github.com/dotconnexion/fxspotify"}


class DeviantArtSetting(WebsiteBaseSetting):
    """Represents the deviantart setting"""

    id = 'deviantart'
    name = 'DeviantArt'
    emoji = discore.config.emoji.deviantart
    proxies = {"fixDeviantArt": "https://github.com/Tschrock/fixdeviantart"}


class NewgroundsSetting(WebsiteBaseSetting):
    """Represents the newgrounds setting"""

    id = 'newgrounds'
    name = 'Newgrounds'
    emoji = discore.config.emoji.newgrounds
    proxies = {"FixNewgrounds": "https://github.com/SauceyRed/fix-newgrounds"}


class MastodonSetting(WebsiteBaseSetting):
    """Represents the mastodon setting"""

    id = 'mastodon'
    name = 'Mastodon'
    emoji = discore.config.emoji.mastodon
    proxies = {"FxMastodon": "https://github.com/Someguy123/fxmastodon"}


class TumblrSetting(WebsiteBaseSetting):
    """Represents the tumblr setting"""

    id = 'tumblr'
    name = 'Tumblr'
    emoji = discore.config.emoji.tumblr
    proxies = {"fxtumblr": "https://github.com/knuxify/fxtumblr"}


class BilibiliSetting(WebsiteBaseSetting):
    """Represents the bilibili setting"""

    id = 'bilibili'
    name = 'BiliBili'
    emoji = discore.config.emoji.bilibili
    proxies = {"BiliFix": "https://www.vxbilibili.com/"}
    is_translation = True


class IFunnySetting(EmbedEZBaseSetting):
    """Represents the ifunny setting"""

    id = 'ifunny'
    name = 'iFunny'
    emoji = discore.config.emoji.ifunny


class FurAffinitySetting(WebsiteBaseSetting):
    """Represents the furaffinity setting"""

    id = 'furaffinity'
    name = 'Fur Affinity'
    emoji = discore.config.emoji.furaffinity
    proxies = {"xfuraffinity": "https://github.com/FirraWoof/xfuraffinity"}


class YouTubeSetting(WebsiteBaseSetting):
    """Represents the youtube setting"""

    id = 'youtube'
    name = 'YouTube'
    emoji = discore.config.emoji.youtube
    proxies = {"Koutube": "https://github.com/iGerman00/koutube"}


class ImgurSetting(EmbedEZBaseSetting):
    """Represents the Imgur setting"""

    id = 'imgur'
    name = 'Imgur'
    emoji = discore.config.emoji.imgur


class LinkedinSetting(WebsiteBaseSetting):
    """Represents the Linkedin setting"""

    id = 'linkedin'
    name = 'LinkedIn'
    emoji = discore.config.emoji.linkedin
    proxies = {"embeds.now": "https://embeds.now/"}

class WeiboSetting(EmbedEZBaseSetting):
    """Represents the Weibo setting"""

    id = 'weibo'
    name = 'Weibo'
    emoji = discore.config.emoji.weibo


class XiaohongshuSetting(EmbedEZBaseSetting):
    """Represents the Xiaohongshu setting"""

    id = 'xiaohongshu'
    name = 'Xiaohongshu'
    emoji = discore.config.emoji.xiaohongshu


class ImageboardsSetting(EmbedEZBaseSetting):
    """Represents the multiple imageboards setting"""

    id = 'imageboards'
    emoji = discore.config.emoji.imageboards
    is_translation = False

    @property
    def name(self):
        return t('settings.imageboards')


class PinterestSetting(EmbedEZBaseSetting):
    """Represents the Pinterest setting"""

    id = 'pinterest'
    name = 'Pinterest'
    emoji = discore.config.emoji.pinterest


class CustomWebsiteModal(Modal):

    def __init__(self, website: CustomWebsite | None, website_setting: CustomWebsitesSetting, **kwargs):
        super().__init__(
            title=t('settings.custom_websites.modal.title'),
            timeout=180,
            **kwargs
        )
        self.website = website
        self.setting = website_setting
        self.name = discore.ui.TextInput(
            placeholder=t('settings.custom_websites.modal.name.placeholder'),
            custom_id='name',
            default=website.name if website else None
        )
        self.domain = discore.ui.TextInput(
            placeholder=t('settings.custom_websites.modal.domain.placeholder'),
            custom_id='domain',
            default=website.domain if website else None
        )
        self.fix_domain = discore.ui.TextInput(
            placeholder=t('settings.custom_websites.modal.fix_domain.placeholder'),
            custom_id='fix_domain',
            default=website.fix_domain if website else None,
            max_length=255
        )
        for field, component in (('name', self.name), ('domain', self.domain), ('fix_domain', self.fix_domain)):
            self.add_item(discore.ui.Label(
                text=t(f'settings.custom_websites.modal.{field}.label'), component=component))

    async def on_submit(self, interaction: discore.Interaction):
        def clean_domain(domain: str) -> str:
            domain = domain.strip()
            if domain.startswith('http://') or domain.startswith('https://'):
                domain = domain.split('://', 1)[1]
            if domain.startswith('www.'):
                domain = domain[4:]
            if domain.endswith('/'):
                domain = domain[:-1]
            return domain

        name_field = self.name.value.strip()
        domain_field = clean_domain(self.domain.value)
        fix_domain_field = clean_domain(self.fix_domain.value)

        if not domain_field or not fix_domain_field:
            await interaction.response.send_message(
                view=notice(t('settings.custom_websites.modal.error.length')), ephemeral=True, delete_after=10)
            return

        custom_website = CustomWebsite.where('guild_id', interaction.guild.id).where({
            'guild_id': interaction.guild.id,
            'domain': domain_field
        }).first()
        if custom_website and (not self.website or custom_website.id != self.website.id):
            await interaction.response.send_message(
                view=notice(t('settings.custom_websites.modal.error.exists')), ephemeral=True, delete_after=10)
            return

        # A website is listed by its name: its domain stands for a blank one
        name_field = name_field or domain_field[:36]

        if len(name_field) > 36:
            await interaction.response.send_message(
                view=notice(t('settings.custom_websites.modal.error.length_name', max=36)), ephemeral=True, delete_after=10)
            return

        if len(domain_field) > 61:
            await interaction.response.send_message(
                view=notice(t('settings.custom_websites.modal.error.length_domain', max=61)), ephemeral=True, delete_after=10)
            return

        values = {
            'name': name_field,
            'domain': domain_field,
            'fix_domain': fix_domain_field
        }
        if self.website:
            self.website.update(values)
            self.setting.custom_websites._items.remove(self.website)
        else:
            self.website = CustomWebsite.create(guild_id=interaction.guild.id, **values)
        self.setting.custom_websites._items.append(self.website)
        self.setting.selected = self.website
        await self.setting.view.refresh(interaction)


class CustomWebsitesSetting(BaseSetting):
    """Represents the custom websites setting"""

    name = 'settings.custom_websites.name'
    id = 'custom_websites'
    description = 'settings.custom_websites.description'
    emoji = '🌐'

    def __init__(self, interaction: discore.Interaction, view: SettingsView, ctx: DataElements):
        super().__init__(interaction, view, ctx)
        self.custom_websites = ctx.guild.custom_websites[:25]
        self.selected: CustomWebsite | None = None

    @property
    async def layout(self) -> List[discore.ui.Item]:
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
        items = [discore.ui.TextDisplay(
            t('settings.custom_websites.content')
            + ((t('settings.custom_websites.list') + website_list) if website_list else '')
        )]

        if self.custom_websites:
            selector = discore.ui.Select(
                options=[
                    discore.SelectOption(
                        label=(website.name.strip() or website.domain)[:100],
                        description=f"{website.domain} → {website.fix_domain}"[:100],
                        value=website.domain,
                        default=website == self.selected
                    )
                    for website in self.custom_websites
                ],
                placeholder=t('settings.custom_websites.placeholder')
            )
            edit_callback(selector, self.view, self.select_action)
            items.append(discore.ui.ActionRow(selector))

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
        items.append(discore.ui.ActionRow(add_button, edit_button, delete_button))
        return items

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
    """Represents the settings website category"""
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
            NewgroundsSetting(interaction, view, ctx),
            MastodonSetting(interaction, view, ctx),
            TumblrSetting(interaction, view, ctx),
            BilibiliSetting(interaction, view, ctx),
            WeiboSetting(interaction, view, ctx),
            XiaohongshuSetting(interaction, view, ctx),
            ImgurSetting(interaction, view, ctx),
            IFunnySetting(interaction, view, ctx),
            YouTubeSetting(interaction, view, ctx),
            LinkedinSetting(interaction, view, ctx),
            FurAffinitySetting(interaction, view, ctx),
            ImageboardsSetting(interaction, view, ctx)
        ))
        self.selected_id: str | None = None
        self.current_page: int = 0

    @property
    def title(self) -> str:
        return self.settings[self.selected_id].title if self.selected_id else super().title

    @property
    async def layout(self) -> List[discore.ui.Item]:
        items = (
            await self.settings[self.selected_id].layout if self.selected_id
            else [discore.ui.TextDisplay(t('settings.websites.content'))]
        )
        options = [await setting.option for setting in self.settings.values()]
        for option in options:
            option.default = option.value == self.selected_id
        placeholder = t('settings.websites.placeholder')

        # A select holds 25 options at most: past that, the websites are listed page by page,
        # the options to change page being part of the list itself
        if len(options) > 25:
            pages = [options[i:i + 23] for i in range(0, len(options), 23)]

            def page_option(page: int, label: str, emoji: str) -> discore.SelectOption:
                return discore.SelectOption(
                    label=t(label), value=f'page:{page}', emoji=emoji,
                    description=t('settings.websites.page', page=page + 1, pages=len(pages)))

            options = pages[self.current_page]
            if self.current_page > 0:
                options.insert(0, page_option(self.current_page - 1, 'settings.websites.previous_page', '⬅️'))
            if self.current_page < len(pages) - 1:
                options.append(page_option(self.current_page + 1, 'settings.websites.next_page', '➡️'))
            placeholder += f" ({t('settings.websites.page', page=self.current_page + 1, pages=len(pages))})"

        website_selection = discore.ui.Select(options=options, placeholder=placeholder)
        edit_callback(website_selection, self.view, self.action)
        return items + [discore.ui.Separator(), discore.ui.ActionRow(website_selection)]

    async def action(self, _, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        value = select.values[0]
        if value.startswith('page:'):
            self.current_page = int(value.removeprefix('page:'))
        else:
            self.selected_id = value
        await self.view.refresh(interaction)


class SettingsView(discore.ui.LayoutView):

    # Errors are reported the same way as in the other views
    on_error = discore.ui.View.on_error

    def __init__(self, i: discore.Interaction):
        super().__init__()

        self.bot: discore.Client = i.client
        self.ctx = DataElements(i)
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
        self.selected_id: str | None = None
        self.timeout_task: asyncio.Task | None = None

    async def interaction_check(self, interaction: discore.Interaction) -> bool:
        # The texts are built from the global locale, which is otherwise only set when a command is invoked
        discore.set_locale(interaction)
        return True

    async def build(self) -> Self:
        """
        Build the interaction response (the whole layout)
        :return: self
        """
        setting = self.settings.get(self.selected_id)

        options = []
        for setting_id in self.settings:
            option = await self.settings[setting_id].option
            if setting_id == self.selected_id:
                option.default = True
            options.append(option)

        parameter_selection = discore.ui.Select(options=options, placeholder=t('settings.placeholder'))
        # noinspection PyTypeChecker
        edit_callback(parameter_selection, self, self.__class__.select_parameter)

        self.clear_items()
        self.add_item(discore.ui.Container(
            discore.ui.TextDisplay(
                f"## {setting.title}" if setting else f"## {t('settings.title')}\n{t('settings.description')}"),
            *(await setting.layout if setting else ()),
            discore.ui.Separator(),
            discore.ui.ActionRow(parameter_selection),
            discore.ui.TextDisplay(footer(self.bot)),
            accent_color=discore.config.color or None
        ))
        self._fit_texts()
        return self

    def _fit_texts(self) -> None:
        """
        Shorten the longest texts until the layout fits in the 4000 characters Discord allows per message
        """
        # This is a plain cut, which may split a markdown element
        texts = [item for item in self.walk_children() if isinstance(item, discore.ui.TextDisplay)]
        excess = self.content_length() - 4000
        for item in sorted(texts, key=lambda text: len(text.content), reverse=True):
            if excess <= 0:
                break
            kept = max(len(item.content) - excess - 1, 0)
            excess -= len(item.content) - kept - 1
            item.content = item.content[:kept] + '…'

    @staticmethod
    async def _message_delete_after(interaction: discore.Interaction, delay: float = 180.0) -> None:
        """
        Task. Automatically delete the interaction response after a delay.
        If the response is already deleted, the function will silently fail.
        This task can be cancelled by calling the cancel() method on the task object.

        :param interaction: The interaction to delete the response of
        :param delay: The delay before deleting the response
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
        """

        self.selected_id = select.values[0]
        await self.refresh(interaction)

    async def reset_timeout(self, interaction: discore.Interaction) -> None:
        """Reset the timeout task"""
        if self.timeout_task is not None:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self._message_delete_after(interaction))

    async def refresh(self, interaction: discore.Interaction) -> None:
        """
        Send or refresh the built view (if already sent) with the current settings
        :param interaction: The interaction to respond to
        """
        await self.build()

        # Discord API sometimes returns incorrect error code, in this case 404 Unknown interaction when interaction
        # is actually found and the message has been sent.
        # Even if the interaction is really not found, there's not much we can do (as the interaction is lost),
        # so in both cases we just ignore the error.
        try:
            # Unlike in embeds, mentions in text components can ping
            if interaction.message is not None:
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(
                    view=self, allowed_mentions=discore.AllowedMentions.none())
            else:
                # noinspection PyUnresolvedReferences
                await interaction.response.send_message(
                    view=self, ephemeral=True, allowed_mentions=discore.AllowedMentions.none())
        except discore.NotFound:
            pass

        await self.reset_timeout(interaction)

    send = refresh
