from __future__ import annotations
from enum import Enum
from typing import Optional

import discore

from utils import *
from views.settings import SettingsView

__all__ = ('Commands',)


class State(Enum):
    WORKING = 0
    PARTIALLY_WORKING = 1
    NOT_WORKING = 2


class Commands(discore.Cog,
               name="commands",
               description="The bot commands"):

    @discore.app_commands.command(
        name="settings",
        description="Manage the fixtweet system settings")
    @discore.app_commands.guild_only()
    @discore.app_commands.default_permissions(manage_messages=True)
    @discore.app_commands.describe(channel="The channel to manage the fixtweet system settings in")
    async def settings(self, i: discore.Interaction, channel: Optional[discore.TextChannel | discore.Thread] = None):
        await SettingsView(i, channel or i.channel).send(i)

    @discore.app_commands.command(
        name="about",
        description="Send information about the bot")
    @discore.app_commands.guild_only()
    async def about(self, i: discore.Interaction):
        embed = discore.Embed(
            title=t('about.name'),
            description=t('about.description'))
        discore.set_embed_footer(self.bot, embed)
        embed.add_field(
            name=t('about.ping.name'),
            value=t('about.ping.value', latency=format(self.bot.latency * 1000, '.0f')),
            inline=False
        )
        embed.add_field(
            name=t('about.help.name'),
            value=t('about.help.value'),
            inline=False
        )
        embed.add_field(
            name=t('about.links.name'),
            value=t('about.links.value', invite_link=discore.config.invite_link),
            inline=False)
        await i.response.send_message(embed=embed)
