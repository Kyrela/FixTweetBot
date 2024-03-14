from enum import Enum

import utils
from typing import Optional

import discord
from discord.ext import commands

__all__ = ('Commands',)


class State(Enum):
    WORKING = 0
    PARTIALLY_WORKING = 1
    NOT_WORKING = 2


class Commands(commands.Cog,
               name="commands",
               description="The bot commands"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="enable",
        description="Enable the fixtweet system for the current server")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(manage_messages=True)
    @discord.app_commands.describe(channel="The channel to enable the fixtweet system in")
    async def enable(self, i: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        channel = channel or i.channel
        embed = discord.Embed(
            title=utils.t('fixtweet.name'),
            description=utils.t('fixtweet.enabled', channel=channel.mention),
            color=0x71aa51
        )
        utils.set_embed_footer(self.bot, embed, set_color=False)

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
            debug_infos.append(utils.t('about.perm.read.disabled'))
        if not send_perm:
            debug_infos.append(utils.t('about.perm.send.disabled'))
        if not embed_perm:
            debug_infos.append(utils.t('about.perm.embed_links.disabled'))
        if not manage_perm:
            debug_infos.append(utils.t('about.perm.manage_messages.disabled'))
        if global_state != State.WORKING:
            embed.add_field(
                name=utils.t('fixtweet.partially_working')
                if global_state == State.PARTIALLY_WORKING else utils.t('fixtweet.not_working'),
                value="\n".join(debug_infos) + "\n" + utils.t('fixtweet.infos'),
                inline=False
            )
            embed.colour = 0xeb8b0c if global_state == State.PARTIALLY_WORKING else 0xd92d43

        if utils.is_fixtweet_enabled(i.guild_id, channel.id):
            embed.description = utils.t('fixtweet.already_enabled', channel=channel.mention)
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        utils.TextChannel.find(channel.id).update({'fix_twitter': True})

        await i.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="disable",
        description="Disable the fixtweet system for the current server")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(manage_messages=True)
    @discord.app_commands.describe(channel="The channel to disable the fixtweet system in")
    async def disable(self, i: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        channel = channel or i.channel
        embed = discord.Embed(
            title=utils.t('fixtweet.name'),
            description=utils.t('fixtweet.disabled', channel=channel.mention),
            color=0x71aa51
        )
        utils.set_embed_footer(self.bot, embed, set_color=False)
        if not utils.is_fixtweet_enabled(i.guild_id, channel.id):
            embed.description = utils.t('fixtweet.already_disabled', channel=channel.mention)
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        utils.TextChannel.find(channel.id).update({'fix_twitter': False})
        await i.response.send_message(embed=embed)

    @discord.app_commands.command(
        name="about",
        description="Send information about the bot")
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(channel="The channel to check the fixtweet system in")
    async def about(self, i: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        channel = channel or i.channel
        embed = discord.Embed(
            title=utils.t('about.name'),
            description=utils.t('about.description'))
        utils.set_embed_footer(self.bot, embed)
        embed.add_field(
            name=utils.t('about.ping'),
            value=f"{self.bot.latency * 1000:.0f} ms",
            inline=False
        )
        enabled = utils.is_fixtweet_enabled(i.guild_id, channel.id)
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
                debug_infos.append(utils.t('about.global.working', channel=channel.mention))
            case State.PARTIALLY_WORKING:
                debug_infos.append(utils.t('about.global.partially_working', channel=channel.mention))
            case State.NOT_WORKING:
                debug_infos.append(utils.t('about.global.not_working', channel=channel.mention))
        debug_infos.append(
            utils.t('about.state.enabled' if enabled else 'about.state.disabled'))
        debug_infos.append(
            utils.t('about.perm.read.enabled' if read_perm else 'about.perm.read.disabled'))
        debug_infos.append(
            utils.t('about.perm.send.enabled' if send_perm else 'about.perm.send.disabled'))
        debug_infos.append(
            utils.t('about.perm.embed_links.enabled' if embed_perm else 'about.perm.embed_links.disabled'))
        debug_infos.append(
            utils.t('about.perm.manage_messages.enabled' if manage_perm else 'about.perm.manage_messages.disabled'))
        embed.add_field(
            name=utils.t('about.debug'),
            value="\n".join(debug_infos),
            inline=False
        )
        embed.add_field(
            name=utils.t('about.links.name'),
            value=utils.t('about.links.value', invite_link=utils.config.invite_link),
            inline=False)
        await i.response.send_message(embed=embed)
