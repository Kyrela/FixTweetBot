from __future__ import annotations
import logging

import discore

from src.utils import *
from src.settings import SettingsView
from database.models.Event import Event

__all__ = ('Commands',)

_logger = logging.getLogger(__name__)


class Commands(discore.Cog,
               name="commands",
               description="The bot commands"):

    def __init__(self, *args, **kwargs):
        if not discore.config.about_command:
            self.__cog_app_commands__.remove(self.about)
            del self.about
            _logger.info("Disabling about command")
        super().__init__(*args, **kwargs)
            

    @discore.app_commands.command(
        name=tstr('settings.command.name'),
        description=tstr('settings.command.description'))
    @discore.app_commands.guild_only()
    @discore.app_commands.default_permissions(manage_messages=True)
    async def settings(self, i: discore.Interaction):
        entrypoint_context.set(f"command settings {{interaction={i!r}}}")
        if discore.config.analytic:
            Event.create({'name': 'command_settings'})
        await SettingsView(i).send(i)

    @discore.app_commands.command(
        name=tstr('about.command.name'),
        description=tstr('about.command.description'))
    @discore.app_commands.guild_only()
    async def about(self, i: discore.Interaction):
        entrypoint_context.set(f"command about {{interaction={i!r}}}")
        if discore.config.analytic:
            Event.create({'name': 'command_about'})
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

        # Discord API sometimes returns incorrect error code, in this case 404 Unknown interaction when interaction
        # is actually found and the message has been sent.
        # Even if the interaction is really not found, there's not much we can do (as the interaction is lost),
        # so in both cases we just ignore the error.
        try:
            await i.response.send_message(embed=embed, view=view)
        except discore.NotFound:
            pass
