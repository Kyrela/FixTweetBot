from __future__ import annotations
from enum import Enum

from discord.app_commands import locale_str

from src.utils import *
from src.settings import SettingsView

__all__ = ('Commands',)


class State(Enum):
    WORKING = 0
    PARTIALLY_WORKING = 1
    NOT_WORKING = 2


class Commands(discore.Cog,
               name="commands",
               description="The bot commands"):

    @discore.app_commands.command(
        name='settings',
        description=tstr('settings.command.description'),
        auto_locale_strings=False)
    @discore.app_commands.guild_only()
    @discore.app_commands.default_permissions(manage_messages=True)
    @discore.app_commands.rename(
        channel=tstr('settings.command.channel.name'),
        member=tstr('settings.command.member.name'),
        role=tstr('settings.command.role.name')
    )
    @discore.app_commands.describe(
        channel=tstr('settings.command.channel.description'),
        member=tstr('settings.command.member.description'),
        role=tstr('settings.command.role.description')
    )
    async def settings(
            self,
            i: discore.Interaction,
            channel: Optional[discore.TextChannel | discore.Thread] = None,
            member: Optional[discore.Member] = None,
            role: Optional[discore.Role] = None,
    ):
        await SettingsView(i, channel or i.channel, member or i.user, role or i.user.top_role).send(i)

    @discore.app_commands.command(
        name='about',
        description=tstr('about.command.description'),
        auto_locale_strings=False)
    @discore.app_commands.guild_only()
    async def about(self, i: discore.Interaction):
        embed = discore.Embed(
            title=t('about.name'),
            description=t('about.description'))
        discore.set_embed_footer(self.bot, embed)
        embed.add_field(
            name=t('about.help.name'),
            value=t('about.help.value'),
            inline=False
        )
        embed.add_field(
            name=t('about.premium.name'),
            value=t(f'about.premium.{str(bool(is_premium(i))).lower()}'),
            inline=False)
        embed.add_field(
            name=t('about.links.name'),
            value=t('about.links.value',
                    invite_link=discore.config.invite_link.format(id=self.bot.application_id),
                    support_link=discore.config.support_link,
                    repo_link=discore.config.repo_link),
            inline=False)
        view = discore.ui.View()
        if not is_premium(i) and is_sku():
            view.add_item(discore.ui.Button(
                style=discore.ButtonStyle.premium,
                sku_id=discore.config.sku
            ))
        view.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.source'),
            url=discore.config.repo_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.github)
        ))
        view.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.invite'),
            url=discore.config.invite_link.format(id=self.bot.application_id),
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.add)
        ))
        view.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.support'),
            url=discore.config.support_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.discord)
        ))

        await i.response.send_message(embed=embed, view=view)
