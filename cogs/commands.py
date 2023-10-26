from enum import Enum

from utils import *
from typing import Optional

import discore

__all__ = ('Commands',)


class State(Enum):
    WORKING = 0
    PARTIALLY_WORKING = 1
    NOT_WORKING = 2


class Commands(discore.Cog,
               name="commands",
               description="The bot commands"):

    @discore.app_commands.command(
        name="enable",
        description="Enable the fixtweet system for the current server")
    @discore.app_commands.guild_only()
    @discore.app_commands.default_permissions(manage_messages=True)
    @discore.app_commands.describe(channel="The channel to enable the fixtweet system in")
    async def enable(self, i: discore.Interaction, channel: Optional[discore.TextChannel] = None):
        channel = channel or i.channel
        embed = discore.Embed(
            title=t('fixtweet.name'),
            description=t('fixtweet.enabled', channel=channel.mention),
            color=0x71aa51
        )
        discore.set_embed_footer(self.bot, embed, set_color=False)

        permissions = channel.permissions_for(i.guild.me)
        read_perm = permissions.read_messages
        send_perm = permissions.send_messages
        embed_perm = permissions.embed_links
        manage_perm = permissions.manage_messages
        global_state = State.WORKING
        if not manage_perm:
            global_state = State.PARTIALLY_WORKING
        if not read_perm or not send_perm or not embed_perm:
            global_state = State.NOT_WORKING
        debug_infos = []
        if not read_perm:
            debug_infos.append(t('about.perm.read.disabled'))
        if not send_perm:
            debug_infos.append(t('about.perm.send.disabled'))
        if not embed_perm:
            debug_infos.append(t('about.perm.embed_links.disabled'))
        if not manage_perm:
            debug_infos.append(t('about.perm.manage_messages.disabled'))
        if global_state != State.WORKING:
            embed.add_field(
                name=t('fixtweet.partially_working') if global_state == State.PARTIALLY_WORKING else t('fixtweet.not_working'),
                value="\n".join(debug_infos) + "\n" + t('fixtweet.infos'),
                inline=False
            )
            embed.colour = 0xeb8b0c if global_state == State.PARTIALLY_WORKING else 0xd92d43

        if is_fixtweet_enabled(i.guild_id, channel.id):
            embed.description = t('fixtweet.already_enabled', channel=channel.mention)
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        data = read_db()
        data["guilds"][str(i.guild_id)]["channels"][str(channel.id)]["fixtweet"] = True
        write_db(data)

        await i.response.send_message(embed=embed)

    @discore.app_commands.command(
        name="disable",
        description="Disable the fixtweet system for the current server")
    @discore.app_commands.guild_only()
    @discore.app_commands.default_permissions(manage_messages=True)
    @discore.app_commands.describe(channel="The channel to disable the fixtweet system in")
    async def disable(self, i: discore.Interaction, channel: Optional[discore.TextChannel] = None):
        channel = channel or i.channel
        embed = discore.Embed(
            title=t('fixtweet.name'),
            description=t('fixtweet.disabled', channel=channel.mention),
            color=0x71aa51
        )
        discore.set_embed_footer(self.bot, embed, set_color=False)
        if not is_fixtweet_enabled(i.guild_id, channel.id):
            embed.description = t('fixtweet.already_disabled', channel=channel.mention)
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        data = read_db()
        data["guilds"][str(i.guild_id)]["channels"][str(channel.id)]["fixtweet"] = False
        write_db(data)
        await i.response.send_message(embed=embed)

    @discore.app_commands.command(
        name="about",
        description="Send information about the bot")
    @discore.app_commands.guild_only()
    @discore.app_commands.describe(channel="The channel to check the fixtweet system in")
    async def about(self, i: discore.Interaction, channel: Optional[discore.TextChannel] = None):
        channel = channel or i.channel
        embed = discore.Embed(
            title=t('about.name'),
            description=t('about.description'))
        discore.set_embed_footer(self.bot, embed)
        embed.add_field(
            name=t('about.ping'),
            value=f"{self.bot.latency * 1000:.0f} ms",
            inline=False
        )
        enabled = is_fixtweet_enabled(i.guild_id, channel.id)
        permissions = channel.permissions_for(i.guild.me)
        read_perm = permissions.read_messages
        send_perm = permissions.send_messages
        embed_perm = permissions.embed_links
        manage_perm = permissions.manage_messages
        global_state = State.WORKING
        if not manage_perm:
            global_state = State.PARTIALLY_WORKING
        if not enabled or not read_perm or not send_perm or not embed_perm:
            global_state = State.NOT_WORKING
        debug_infos = []
        match global_state:
            case State.WORKING:
                debug_infos.append(t('about.global.working', channel=channel.mention))
            case State.PARTIALLY_WORKING:
                debug_infos.append(t('about.global.partially_working', channel=channel.mention))
            case State.NOT_WORKING:
                debug_infos.append(t('about.global.not_working', channel=channel.mention))
        debug_infos.append(
            t('about.state.enabled' if enabled else 'about.state.disabled'))
        debug_infos.append(
            t('about.perm.read.enabled' if read_perm else 'about.perm.read.disabled'))
        debug_infos.append(
            t('about.perm.send.enabled' if send_perm else 'about.perm.send.disabled'))
        debug_infos.append(
            t('about.perm.embed_links.enabled' if embed_perm else 'about.perm.embed_links.disabled'))
        debug_infos.append(
            t('about.perm.manage_messages.enabled' if manage_perm else 'about.perm.manage_messages.disabled'))
        embed.add_field(
            name=t('about.debug'),
            value="\n".join(debug_infos),
            inline=False
        )
        embed.add_field(
            name=t('about.links.name'),
            value=t('about.links.value', invite_link=discore.config.invite_link),
            inline=False)
        await i.response.send_message(embed=embed)
