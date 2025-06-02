"""
Settings view for the bot
"""

from __future__ import annotations
import asyncio
from typing import Type, List, Self, overload

from database.models.Role import Role
from database.models.TextChannel import *
from database.models.Guild import *
from database.models.Member import *
from database.models.CustomWebsite import CustomWebsite

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

    proxy_name: str
    proxy_url: str

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.db_guild = Guild.find_or_create(interaction.guild.id)
        self.state = bool(self.db_guild[self.id])
        if f'{self.id}_view' in self.db_guild.get_columns():
            self.is_view = True
            self.view_state = self.db_guild[f'{self.id}_view']
            enum_name = f'{self.id.title()}View'
            self.view_enum = getattr(__import__('database.models.Guild', fromlist=[enum_name]), enum_name)
        else:
            self.is_view = False
            self.view_state = None
            self.view_enum = None
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {self.name}",
            description=t(
                f'settings.base_website.content',
                name=self.name,
                state=t(f'settings.base_website.state.{str(self.state).lower()}', name=self.name),
                view=(
                        '\n' + t(f'settings.base_website.view.{self.view_state.name.lower()}.emoji')
                        + ' ' + t(f'settings.base_website.view.{self.view_state.name.lower()}.label'))
                if self.view_state else '',
                credits=f"[{self.proxy_name}](<{self.proxy_url}>)"
            )
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        item = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.base_website.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
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
            return [item, view_selector]

        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.db_guild.update({self.id: self.state})
        await view.refresh(interaction)

    async def view_action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        if not self.is_view:
            await view.refresh(interaction)
            return
        self.view_state = self.view_enum[select.values[0]]
        self.db_guild.update({f'{self.id}_view': self.view_state.value})
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + self.name,
            value=self.id,
            description=t('settings.base_website.description', name=self.name),
            emoji=self.emoji
        )


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

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            channel: discore.TextChannel | discore.Thread,
            member: discore.Member,
            role: discore.Role
    ):
        self.channel = channel
        self.interaction = interaction
        self.member = member
        self.role = role
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        db_guild = Guild.find_or_create(self.channel.guild.id)
        db_channel = TextChannel.find_or_create(db_guild, self.channel.id)
        db_member = Member.find_or_create(self.member, db_guild)
        db_role = Role.find_or_create(db_guild, self.role.id)
        db_roles = Role.finds_or_creates(db_guild, [role.id for role in self.member.roles])
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
        if isinstance(self.channel, discore.Thread):
            perms.append('send_messages_in_threads')
        if db_guild.original_message != OriginalMessage.NOTHING:
            perms.append('manage_messages')
        if db_guild.reply:
            perms.append('read_message_history')
        embed.add_field(
            name=t('settings.troubleshooting.permissions', channel=self.channel.mention),
            value=format_perms(perms, self.channel, include_label=False, include_valid=True),
            inline=False
        )
        options = [
            ('channel', self.channel, db_channel.enabled),
            ('member', self.member, db_member.enabled),
            ('webhooks', None, db_guild.webhooks),
            ('role', self.role, db_role.enabled),
        ]
        for role in self.member.roles:
            db_role = next((r for r in db_roles if r.id == role.id), None)
            if db_role and role != self.role:
                options.append(('role', role, db_role.enabled))

        str_options_fields = group_join(
            [
                '- ' + t(f'settings.{key}.state.{str(db_value).lower()}',
                         **{key: discord_value.mention if discord_value else None})
                for key, discord_value, db_value in options],
            1024
        )

        for i, str_options in enumerate(str_options_fields):
            embed.add_field(
                name=t('settings.troubleshooting.options') + (f' ({i+1})' if i+1 > 1 else ''),
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
            'pixiv': 'Pixiv',
            'twitch': 'Twitch',
            'spotify': 'Spotify',
            'deviantart': 'DeviantArt',
            'mastodon': 'Mastodon',
            'tumblr': 'Tumblr',
            'bilibili': 'BiliBili',
            'ifunny': 'iFunny',
            'furaffinity': 'Fur Affinity',
            'youtube': 'YouTube'
        }
        str_websites = "\n".join([
            '- ' + t(f'settings.base_website.state.{str(bool(db_guild[key])).lower()}', name=value)
            for key, value in websites.items()
        ])
        embed.add_field(
            name=t('settings.troubleshooting.websites'),
            value=str_websites,
            inline=False
        )
        if db_guild.custom_websites:
            str_custom_websites = "\n".join([
                f"- `{website.domain}`"
                for website in db_guild.custom_websites
            ])
            embed.add_field(
                name=t('settings.troubleshooting.custom_websites'),
                value=str_custom_websites,
                inline=False
            )
        embed.add_field(
            name=t('settings.troubleshooting.premium.name'),
            value=t(f'settings.troubleshooting.premium.{str(bool(is_premium(self.interaction))).lower()}'),
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
        return (
            [refresh_button, support]
            if is_premium(self.interaction) or not is_sku()
            else [refresh_button, premium_button, support]
        )

    async def refresh_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.interaction = interaction
        await view.refresh(interaction)


class ChannelSetting(BaseSetting):
    """
    Represents the channel setting
    """

    name = 'settings.channel.name'
    id = 'channel'
    description = 'settings.channel.description'
    emoji = '#️⃣'

    def __init__(
            self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel | discore.Thread):
        self.guild = channel.guild
        self.db_guild = Guild.find_or_create(self.guild.id)
        self.db_channel = TextChannel.find_or_create(self.db_guild, channel.id)
        self.channel = channel
        self.state = self.db_channel.enabled
        self.default_state = self.db_guild.default_channel_state
        self.all_state = None
        self.perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(channel, discore.Thread):
            self.perms.append('send_messages_in_threads')
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        if self.all_state is not None:
            state = t(f'settings.channel.all_state.{str(self.all_state).lower()}')
        else:
            state = t(f'settings.channel.state.{str(self.state).lower()}', channel=self.channel.mention)
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=
            t('settings.channel.content',
              channel=self.channel.mention,
              bot=self.bot.user.display_name,
              state=state,
              default_state=t(f'settings.channel.default_state.{str(self.default_state).lower()}'),
              perms=format_perms(self.perms, self.channel))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        toggle_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.channel.toggle.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(toggle_button, self.view, self.toggle)
        toggle_all_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.all_state else discore.ButtonStyle.secondary,
            label=t(f'settings.channel.toggle_all.{str(self.all_state).lower()}'),
            custom_id='channel_all'
        )
        edit_callback(toggle_all_button, self.view, self.toggle_all)
        if is_premium(self.interaction):
            toggle_default_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.default_state else discore.ButtonStyle.secondary,
                label=t(f'settings.channel.toggle_default.{str(self.default_state).lower()}'),
                custom_id='channel_default'
            )
        else:
            toggle_default_button = discore.ui.Button(
                label=t('settings.channel.toggle_default.premium'),
                disabled=True
            )
        edit_callback(toggle_default_button, self.view, self.toggle_default)
        return [toggle_button, toggle_all_button, toggle_default_button]

    async def toggle(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.all_state = None
        self.db_channel.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_all(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.all_state = not self.all_state
        self.state = self.all_state
        TextChannel.update_guild_channels(self.guild, [self.channel.id], self.db_guild.default_channel_state)
        TextChannel.where(
            'guild_id', self.guild.id).where('id', '!=', self.channel.id).update({'enabled': self.all_state})

        self.db_channel.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_default(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if not is_premium(interaction):
            return
        self.default_state = not self.default_state
        self.db_guild.update({'default_channel_state': self.default_state})
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=(('⚠️ ' if is_missing_perm(self.perms, self.channel) else '🟢 ')
                   if self.state else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )


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
        option_tr_path = f'settings.original_message.option.{self.state.name.lower()}'
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.original_message.content',
                state=t(option_tr_path + '.emoji') + ' ' + t(option_tr_path + '.label'),
                channel=self.channel.mention,
                perms=format_perms(
                    ['manage_messages']
                    if self.state != OriginalMessage.NOTHING
                    else [],
                    self.channel))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('⚠️ '
                   if self.state != OriginalMessage.NOTHING and is_missing_perm(['manage_messages'], self.channel)
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.reply_to_message = bool(db_guild.reply_to_message)
        self.reply_silently = bool(db_guild.reply_silently)
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        perms = [
            'view_channel',
            'send_messages',
            'embed_links'
        ]
        if isinstance(self.channel, discore.Thread):
            perms.append('send_messages_in_threads')
        if self.reply_to_message:
            perms.append('read_message_history')
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.reply_method.content',
                state=t(f'settings.reply_method.state.{str(self.reply_to_message).lower()}', emoji=self.emoji),
                silent=t(f'settings.reply_method.silent.{str(self.reply_silently).lower()}'),
                perms=format_perms(perms, self.channel))
        )
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('⚠️ ' if self.reply_to_message and is_missing_perm(['read_message_history'], self.channel) else '')
                  + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )

    @property
    async def items(self) -> List[discore.ui.Item]:
        reply_to_message_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.reply_to_message else discore.ButtonStyle.secondary,
            label=t(f'settings.reply_method.button.{str(self.reply_to_message).lower()}'),
            custom_id=self.id
        )
        edit_callback(reply_to_message_button, self.view, self.toggle_reply_to_message)
        reply_silently_button = discore.ui.Button(
            style=discore.ButtonStyle.secondary if self.reply_silently else discore.ButtonStyle.primary,
            label=t(f'settings.reply_method.silent.{str(self.reply_silently).lower()}'),
            custom_id='reply_silently'
        )
        edit_callback(reply_silently_button, self.view, self.toggle_reply_silently)
        return [reply_to_message_button, reply_silently_button]

    async def toggle_reply_to_message(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_to_message = not self.reply_to_message
        self.db_guild.update({'reply': self.reply_to_message})
        await view.refresh(interaction)

    async def toggle_reply_silently(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.reply_silently = not self.reply_silently
        self.db_guild.update({'reply_silently': self.reply_silently})
        await view.refresh(interaction)


class WebhooksSetting(BaseSetting):
    """
    Represents the
    """

    name = 'settings.webhooks.name'
    id = 'webhooks'
    description = 'settings.webhooks.description'
    emoji = discore.config.emoji.webhooks

    def __init__(self, interaction: discore.Interaction, view: SettingsView, channel: discore.TextChannel):
        db_guild = Guild.find_or_create(channel.guild.id)
        self.db_guild = db_guild
        self.channel = channel
        self.state = bool(db_guild.webhooks)
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.webhooks.content',
                state=t(f'settings.webhooks.state.{str(self.state).lower()}'))
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
            label=t(f'settings.webhooks.button.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(item, self.view, self.action)
        return [item]

    async def action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.db_guild.update({'webhooks': self.state})
        await view.refresh(interaction)


class TwitterTranslationModal(discore.ui.Modal):

    def __init__(self, twitter_setting: TwitterSetting, lang: str, **kwargs):
        super().__init__(
            title=t('settings.twitter.modal.title'),
            timeout=180,
            **kwargs
        )
        self.setting = twitter_setting
        self.lang = lang
        self.add_item(discore.ui.TextInput(
            label=t('settings.twitter.modal.label'),
            placeholder=t('settings.twitter.modal.placeholder'),
            custom_id='lang',
            default=lang
        ))

    async def on_submit(self, interaction: discore.Interaction):
        lang = str(self.children[0])
        if len(lang) != 2:
            await interaction.response.send_message(
                t('settings.twitter.modal.error', lang=lang), ephemeral=True, delete_after=10)
            return
        self.setting.lang = lang
        self.setting.db_guild.update({'twitter_tr_lang': lang})
        await self.setting.view.refresh(interaction)


class TwitterSetting(BaseSetting):
    """
    Represents the twitter setting
    """

    name = 'settings.twitter.name'
    id = 'twitter'
    description = 'settings.twitter.description'
    emoji = discore.config.emoji.twitter

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.db_guild = Guild.find_or_create(interaction.guild.id)
        self.state = bool(self.db_guild.twitter)
        self.view_state = self.db_guild.twitter_view
        self.translation = self.db_guild.twitter_tr
        self.lang = self.db_guild.twitter_tr_lang
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.twitter.content',
                state=t(
                    f'settings.twitter.state.{str(self.state).lower()}'
                ) + t(
                    f'settings.twitter.translation.{str(self.translation).lower()}',
                    lang=self.lang
                ),
                view=t(f'settings.base_website.view.{self.view_state.name.lower()}.emoji')
                + ' ' + t(f'settings.base_website.view.{self.view_state.name.lower()}.label'),
                credits=f"[FxTwitter](<https://github.com/FixTweet/FxTwitter>)"
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
        edit_callback(toggle_button, self.view, self.toggle_action)
        translation_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.translation and self.state else discore.ButtonStyle.secondary,
            label=t(
                f'settings.twitter.button.translation.{str(bool(self.translation and self.state)).lower()}',
                lang=self.lang
            ),
            custom_id='twitter_translation',
            disabled=not self.state
        )
        edit_callback(translation_button, self.view, self.translation_action)
        translation_lang_button = discore.ui.Button(
            label=t('settings.twitter.button.translation_lang'),
            custom_id='twitter_translation_lang',
            disabled=not (self.translation and self.state)
        )
        edit_callback(translation_lang_button, self.view, self.translation_lang_action)
        view_selector = discore.ui.Select(
            options=[
                discore.SelectOption(
                    label=t(f'settings.base_website.view.{view.name.lower()}.label'),
                    emoji=t(f'settings.base_website.view.{view.name.lower()}.emoji'),
                    value=view.name,
                    default=view == self.view_state,
                )
                for view in TwitterView
            ]
        )
        edit_callback(view_selector, self.view, self.view_action)
        return [toggle_button, translation_button, translation_lang_button, view_selector]

    async def toggle_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.db_guild.update({'twitter': self.state})
        await view.refresh(interaction)

    async def translation_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.translation = not self.translation
        if self.db_guild.twitter_tr_lang is None:
            # noinspection PyUnresolvedReferences
            self.lang = interaction.locale.value.split('-')[0]
        self.db_guild.update({'twitter_tr': self.translation, 'twitter_tr_lang': self.lang})
        await view.refresh(interaction)

    async def translation_lang_action(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        await self.view.reset_timeout(interaction)
        # noinspection PyUnresolvedReferences
        await interaction.response.send_modal(TwitterTranslationModal(self, self.lang))

    async def view_action(self, view: SettingsView, interaction: discore.Interaction, select: discore.ui.Select) -> None:
        self.view_state = TwitterView[select.values[0]]
        self.db_guild.update({'twitter_view': self.view_state.value})
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )


class InstagramSetting(WebsiteBaseSetting):
    """
    Represents the instagram setting
    """

    id = 'instagram'
    name = 'Instagram'
    emoji = discore.config.emoji.instagram
    proxy_name = "EmbedEZ"
    proxy_url = "https://embedez.com"


class TikTokSetting(WebsiteBaseSetting):
    """
    Represents the tiktok setting
    """

    id = 'tiktok'
    name = 'TikTok'
    emoji = discore.config.emoji.tiktok
    proxy_name = "fxTikTok"
    proxy_url = "https://github.com/okdargy/fxTikTok"


class RedditSetting(WebsiteBaseSetting):
    """
    Represents the reddit setting
    """

    id = 'reddit'
    name = 'Reddit'
    emoji = discore.config.emoji.reddit
    proxy_name = "vxreddit"
    proxy_url = "https://github.com/dylanpdx/vxReddit"


class ThreadsSetting(WebsiteBaseSetting):
    """
    Represents the threads setting
    """

    id = 'threads'
    name = 'Threads'
    emoji = discore.config.emoji.threads
    proxy_name = "FixThreads"
    proxy_url = "https://github.com/milanmdev/fixthreads"


class BlueskySetting(WebsiteBaseSetting):
    """
    Represents the bluesky setting
    """

    id = 'bluesky'
    name = 'Bluesky'
    emoji = discore.config.emoji.bluesky
    proxy_name = "VixBluesky"
    proxy_url = "https://github.com/Lexedia/VixBluesky"


class SnapchatSetting(WebsiteBaseSetting):
    """
    Represents the snapchat setting
    """

    id = 'snapchat'
    name = 'Snapchat'
    emoji = discore.config.emoji.snapchat
    proxy_name = "EmbedEZ"
    proxy_url = "https://embedez.com"


class FacebookSetting(WebsiteBaseSetting):
    """
    Represents the facebook setting
    """

    id = 'facebook'
    name = 'Facebook'
    emoji = discore.config.emoji.facebook
    proxy_name = "EmbedEZ"
    proxy_url = "https://embedez.com"


class PixivSetting(WebsiteBaseSetting):
    """
    Represents the pixiv setting
    """

    id = 'pixiv'
    name = 'Pixiv'
    emoji = discore.config.emoji.pixiv
    proxy_name = "phixiv"
    proxy_url = "https://github.com/thelaao/phixiv"


class TwitchSetting(WebsiteBaseSetting):
    """
    Represents the twitch setting
    """

    id = 'twitch'
    name = 'Twitch'
    emoji = discore.config.emoji.twitch
    proxy_name = "fxtwitch"
    proxy_url = "https://github.com/seriaati/fxtwitch"


class SpotifySetting(WebsiteBaseSetting):
    """
    Represents the spotify setting
    """

    id = 'spotify'
    name = 'Spotify'
    emoji = discore.config.emoji.spotify
    proxy_name = "fxtwitch"
    proxy_url = "https://github.com/dotconnexion/fxspotify"


class DeviantArtSetting(WebsiteBaseSetting):
    """
    Represents the deviantart setting
    """

    id = 'deviantart'
    name = 'DeviantArt'
    emoji = discore.config.emoji.deviantart
    proxy_name = "fixDeviantArt"
    proxy_url = "https://github.com/Tschrock/fixdeviantart"


class MastodonSetting(WebsiteBaseSetting):
    """
    Represents the mastodon setting
    """

    id = 'mastodon'
    name = 'Mastodon'
    emoji = discore.config.emoji.mastodon
    proxy_name = "FxMastodon"
    proxy_url = "https://fx.zillanlabs.tech/"


class TumblrSetting(WebsiteBaseSetting):
    """
    Represents the tumblr setting
    """

    id = 'tumblr'
    name = 'Tumblr'
    emoji = discore.config.emoji.tumblr
    proxy_name = "fxtumblr"
    proxy_url = "https://github.com/knuxify/fxtumblr"


class BilibiliSetting(WebsiteBaseSetting):
    """
    Represents the bilibili setting
    """

    id = 'bilibili'
    name = 'BiliBili'
    emoji = discore.config.emoji.bilibili
    proxy_name = "BiliFix"
    proxy_url = "https://www.vxbilibili.com/"


class IFunnySetting(WebsiteBaseSetting):
    """
    Represents the ifunny setting
    """

    id = 'ifunny'
    name = 'iFunny'
    emoji = discore.config.emoji.ifunny
    proxy_name = "EmbedEZ"
    proxy_url = "https://embedez.com"


class FurAffinitySetting(WebsiteBaseSetting):
    """
    Represents the furaffinity setting
    """

    id = 'furaffinity'
    name = 'Fur Affinity'
    emoji = discore.config.emoji.furaffinity
    proxy_name = "xfuraffinity"
    proxy_url = "https://github.com/FirraWoof/xfuraffinity"


class YouTubeSetting(WebsiteBaseSetting):
    """
    Represents the youtube setting
    """

    id = 'youtube'
    name = 'YouTube'
    emoji = discore.config.emoji.youtube
    proxy_name = "Koutube"
    proxy_url = "https://github.com/iGerman00/koutube"


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
                t('settings.custom_websites.modal.error.exists', website=domain_field), ephemeral=True, delete_after=10)
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
            self.website = self.website.update({
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        self.db_guild = Guild.find_or_create(interaction.guild.id)
        self.custom_websites = self.db_guild.custom_websites[:25]
        self.selected: Optional[CustomWebsite] = None
        super().__init__(interaction, view)

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


class MemberSetting(BaseSetting):
    """
    Represents the member setting
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
        self.guild = channel.guild
        self.db_guild = Guild.find_or_create(self.guild.id)
        self.db_member = Member.find_or_create(member, self.db_guild)
        self.member = member
        self.state = self.db_member.enabled
        self.default_state = self.db_guild.default_member_state
        self.all_state = None
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        if self.all_state is not None:
            state = t(f'settings.member.all_state.{str(self.all_state).lower()}')
        else:
            state = t(f'settings.member.state.{str(self.state).lower()}', member=self.member.mention)
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.member.content',
                member=self.member.mention,
                bot=self.bot.user.display_name,
                state=state,
                default_state=t(f'settings.member.default_state.{str(self.default_state).lower()}')
            ))
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        toggle_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.member.toggle.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(toggle_button, self.view, self.toggle)
        toggle_all_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.all_state else discore.ButtonStyle.secondary,
            label=t(f'settings.member.toggle_all.{str(self.all_state).lower()}'),
            custom_id='member_all'
        )
        edit_callback(toggle_all_button, self.view, self.toggle_all)
        if is_premium(self.interaction):
            toggle_default_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.default_state else discore.ButtonStyle.secondary,
                label=t(f'settings.member.toggle_default.{str(self.default_state).lower()}'),
                custom_id='member_default'
            )
        else:
            toggle_default_button = discore.ui.Button(
                label=t('settings.member.toggle_default.premium'),
                disabled=True
            )
        edit_callback(toggle_default_button, self.view, self.toggle_default)
        return [toggle_button, toggle_all_button, toggle_default_button]

    async def toggle(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.all_state = None
        self.db_member.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_all(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.all_state = not self.all_state
        Member.update_guild_members(self.guild, [self.member.id], self.db_guild.default_member_state)
        (Member.
         where('guild_id', self.guild.id).
         where('user_id', '!=', self.member.id).
         where('bot', False).
         update({'enabled': self.all_state}))

        self.state = self.all_state
        self.db_member.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_default(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if not is_premium(interaction):
            return
        self.default_state = not self.default_state
        self.db_guild.update({'default_member_state': self.default_state})
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + t(self.name),
            value=self.id,
            description=t(self.description),
            emoji=self.emoji
        )


class RoleSetting(BaseSetting):
    """
    Represents the role setting
    """

    name = 'settings.role.name'
    id = 'role'
    description = 'settings.role.description'
    emoji = discore.config.emoji.role

    def __init__(
            self,
            interaction: discore.Interaction,
            view: SettingsView,
            channel: discore.TextChannel | discore.Thread,
            role: discore.Role
    ):
        self.guild = channel.guild
        self.db_guild = Guild.find_or_create(self.guild.id)
        self.db_role = Role.find_or_create(self.db_guild, role.id)
        self.role = role
        self.state = self.db_role.enabled
        self.default_state = self.db_guild.default_role_state
        self.all_state = None
        super().__init__(interaction, view)

    @property
    async def embed(self) -> discore.Embed:
        if self.all_state is not None:
            state = t(f'settings.role.all_state.{str(self.all_state).lower()}')
        else:
            state = t(f'settings.role.state.{str(self.state).lower()}', role=self.role.mention)
        embed = discore.Embed(
            title=f"{self.emoji} {t(self.name)}",
            description=t(
                'settings.role.content',
                role=self.role.mention,
                bot=self.bot.user.display_name,
                state=state,
                default_state=t(f'settings.role.default_state.{str(self.default_state).lower()}')
            ))
        discore.set_embed_footer(self.bot, embed)
        return embed

    @property
    async def items(self) -> List[discore.ui.Item]:
        toggle_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.state else discore.ButtonStyle.secondary,
            label=t(f'settings.role.toggle.{str(self.state).lower()}'),
            custom_id=self.id
        )
        edit_callback(toggle_button, self.view, self.toggle)
        toggle_all_button = discore.ui.Button(
            style=discore.ButtonStyle.primary if self.all_state else discore.ButtonStyle.secondary,
            label=t(f'settings.role.toggle_all.{str(self.all_state).lower()}'),
            custom_id='role_all'
        )
        edit_callback(toggle_all_button, self.view, self.toggle_all)
        if is_premium(self.interaction):
            toggle_default_button = discore.ui.Button(
                style=discore.ButtonStyle.primary if self.default_state else discore.ButtonStyle.secondary,
                label=t(f'settings.role.toggle_default.{str(self.default_state).lower()}'),
                custom_id='role_default'
            )
        else:
            toggle_default_button = discore.ui.Button(
                label=t('settings.role.toggle_default.premium'),
                disabled=True
            )
        edit_callback(toggle_default_button, self.view, self.toggle_default)
        return [toggle_button, toggle_all_button, toggle_default_button]

    async def toggle(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.state = not self.state
        self.all_state = None
        self.db_role.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_all(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        self.all_state = not self.all_state
        Role.update_guild_roles(self.guild, [self.role.id], self.db_guild.default_role_state)
        Role.where(
            'guild_id', self.guild.id).where('id', '!=', self.role.id).update({'enabled': self.all_state})
        self.state = self.all_state
        self.db_role.update({'enabled': self.state})
        await view.refresh(interaction)

    async def toggle_default(self, view: SettingsView, interaction: discore.Interaction, _) -> None:
        if not is_premium(interaction):
            return
        self.default_state = not self.default_state
        self.db_guild.update({'default_role_state': self.default_state})
        await view.refresh(interaction)

    @property
    async def option(self) -> discore.SelectOption:
        return discore.SelectOption(
            label=('🟢 ' if self.state else '🔴 ') + t(self.name),
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

    def __init__(self, interaction: discore.Interaction, view: SettingsView):
        super().__init__(interaction, view)
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            CustomWebsitesSetting(interaction, view),
            TwitterSetting(interaction, view),
            InstagramSetting(interaction, view),
            TikTokSetting(interaction, view),
            RedditSetting(interaction, view),
            ThreadsSetting(interaction, view),
            BlueskySetting(interaction, view),
            SnapchatSetting(interaction, view),
            FacebookSetting(interaction, view),
            PixivSetting(interaction, view),
            TwitchSetting(interaction, view),
            SpotifySetting(interaction, view),
            DeviantArtSetting(interaction, view),
            MastodonSetting(interaction, view),
            TumblrSetting(interaction, view),
            BilibiliSetting(interaction, view),
            IFunnySetting(interaction, view),
            YouTubeSetting(interaction, view),
            FurAffinitySetting(interaction, view),
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

    def __init__(
            self,
            i: discore.Interaction,
            channel: discore.TextChannel | discore.Thread,
            member: discore.Member,
            role: discore.Role
    ):
        super().__init__()

        self.bot: discore.Bot = i.client
        self.channel: discore.TextChannel | discore.Thread = channel
        self.member: discore.Member = member
        self.embed: Optional[discore.Embed] = None
        self.settings: dict[str, BaseSetting] = BaseSetting.dict_from_settings((
            TroubleshootingSetting(i, self, channel, member, role),
            ChannelSetting(i, self, channel),
            MemberSetting(i, self, channel, member),
            RoleSetting(i, self, channel, role),
            WebsiteSettings(i, self),
            OriginalMessageBehaviorSetting(i, self, channel),
            ReplyMethodSetting(i, self, channel),
            WebhooksSetting(i, self, channel),
        ))
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
