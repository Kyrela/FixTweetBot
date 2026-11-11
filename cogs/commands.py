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
        await Event.buff_cr({'name': 'command_settings'})
        await SettingsView(i).send(i)

    @discore.app_commands.command(
        name=tstr('about.command.name'),
        description=tstr('about.command.description'))
    @discore.app_commands.guild_only()
    async def about(self, i: discore.Interaction):
        entrypoint_context.set(f"command about {{interaction={i!r}}}")
        await Event.buff_cr({'name': 'command_about'})
        links = discore.ui.ActionRow()
        if not is_premium(i) and is_sku():
            links.add_item(discore.ui.Button(
                style=discore.ButtonStyle.premium,
                sku_id=discore.config.sku
            ))
        links.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.source'),
            url=discore.config.repo_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.github)
        ))
        links.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.invite'),
            url=discore.config.invite_link.format(id=self.bot.application_id),
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.add)
        ))
        links.add_item(discore.ui.Button(
            style=discore.ButtonStyle.link,
            label=t('about.support'),
            url=discore.config.support_link,
            emoji=discore.PartialEmoji.from_str(discore.config.emoji.discord)
        ))
        view = discore.ui.LayoutView()
        view.add_item(discore.ui.Container(
            discore.ui.Section(
                f"## {t('about.name')}\n{t('about.description')}",
                accessory=discore.ui.Thumbnail(self.bot.user.display_avatar.url)),
            discore.ui.Separator(),
            discore.ui.TextDisplay(
                f"### {t('about.help.name')}\n" + t(
                    'about.help.value',
                    settings_command='/' + t('settings.command.name'),
                    support_link=discore.config.support_link,
                    troubleshooting_section=t('settings.troubleshooting.name'))),
            discore.ui.TextDisplay(
                f"### {t('about.premium.name')}\n" + t(f'about.premium.{str(bool(is_premium(i))).lower()}')),
            discore.ui.TextDisplay(
                f"### {t('about.links.name')}\n" + t(
                    'about.links.value',
                    invite_link=discore.config.invite_link.format(id=self.bot.application_id),
                    topgg_link=discore.config.topgg_link.format(id=self.bot.user.id),
                    repo_link=discore.config.repo_link,
                    translation_link=discore.config.translation_link,
                    credits_link=discore.config.repo_link + "/blob/v" + discore.config.version + "/README.md#credits",
                    support_link=discore.config.support_link)),
            discore.ui.Separator(),
            links,
            discore.ui.TextDisplay(footer(self.bot)),
            accent_color=discore.config.color or None
        ))

        # Discord API sometimes returns incorrect error code, in this case 404 Unknown interaction when interaction
        # is actually found and the message has been sent.
        # Even if the interaction is really not found, there's not much we can do (as the interaction is lost),
        # so in both cases we just ignore the error.
        try:
            await i.response.send_message(view=view, allowed_mentions=discore.AllowedMentions.none())
        except discore.NotFound:
            pass
