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
        name="bug",
        description="Report a bug report to the developer")
    @discore.app_commands.describe(
        report="The description of the bug",
        attachment="An attachment to the bug report (like a screenshot)")
    async def bug(self, i: discore.Interaction, report: str, attachment: Optional[discore.Attachment] = None):
        await self.report(i, report, False, attachment)

    @discore.app_commands.command(
        name="suggest",
        description="Send a suggestion to the developer")
    @discore.app_commands.describe(
        suggestion="The suggestion to send",
        attachment="An attachment to the suggestion (like a screenshot)")
    async def suggest(self, i: discore.Interaction, suggestion: str, attachment: Optional[discore.Attachment] = None):
        await self.report(i, suggestion, True, attachment)

    async def report(
            self, i: discore.Interaction, message: str, is_suggestion: bool, attachment: discore.Attachment = None):
        embed = discore.Embed(description=message, colour=discore.config.color)
        embed.set_author(name=("Suggestion" if is_suggestion else "Report") + f" de {i.user.name}",
                         icon_url=i.user.avatar.url)
        discore.set_embed_footer(self.bot, embed)
        channel_id = discore.config.suggestions.channel if is_suggestion else discore.config.log.channel
        await self.bot.get_channel(channel_id).send(
            embed=embed,
            files=[await attachment.to_file()] if attachment else [])
        await i.response.send_message(
            (t('report.suggestion') if is_suggestion else t('report.bug')) + t('report.send_confirmation'))

    class ChangelogView(discore.ui.View):

        def __init__(self, bot: discore.Client):
            super().__init__()
            self.bot = bot
            self.page = 0
            self.changelog = t('changelog.versions')

        async def send(self, interaction: discore.Interaction):
            self.update_buttons()
            await interaction.response.send_message(embed=self.create_embed(), view=self)

        async def update(self, interaction: discore.Interaction):
            self.update_buttons()
            await interaction.message.edit(embed=self.create_embed(), view=self)

        def update_buttons(self):
            if self.page == 0:
                self.prev_button.disabled = True
                self.prev_button.label = "|<"
            else:
                self.prev_button.disabled = False
                self.prev_button.label = f"< {t('changelog.page')} {self.page}"

            if self.page == len(self.changelog) - 1:
                self.next_button.disabled = True
                self.next_button.label = ">|"
            else:
                self.next_button.disabled = False
                self.next_button.label = f"{t('changelog.page')} {self.page + 2} >"

            self.page_button.label = (
                f"{t('changelog.name')} | {t('changelog.page')} {self.page + 1}/{len(self.changelog)}")

        def create_embed(self):
            page_data = self.changelog[self.page]
            if isinstance(page_data, dict):
                embed = discore.Embed(
                    title=page_data["name"],
                    description=page_data["value"],
                    color=discore.config.color)
            else:
                embed = discore.Embed(
                    title=page_data[0],
                    color=discore.config.color)
                for field in page_data[1:]:
                    field["inline"] = False
                    embed.add_field(**field)
            discore.set_embed_footer(self.bot, embed)
            return embed

        @discore.ui.button(label="|<", style=discore.ButtonStyle.primary, disabled=True)
        async def prev_button(self, interaction: discore.Interaction, button: discore.ui.Button):
            await interaction.response.defer()
            self.page -= 1
            await self.update(interaction)

        @discore.ui.button(label=f"Changelog", style=discore.ButtonStyle.gray, disabled=True)
        async def page_button(self, interaction: discore.Interaction, button: discore.ui.Button):
            pass

        @discore.ui.button(label="Page 2 >", style=discore.ButtonStyle.primary)
        async def next_button(self, interaction: discore.Interaction, button: discore.ui.Button):
            await interaction.response.defer()
            self.page += 1
            await self.update(interaction)

    @discore.app_commands.command(
        name="changelog",
        description="Send the list of changes for each version of the bot")
    async def changelog(self, i: discore.Interaction):
        await self.ChangelogView(self.bot).send(i)

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
