import logging
import asyncio
import json
import aiohttp


from src import utils
from database.models.Event import *

import discore

__all__ = ('Setup',)

_logger = logging.getLogger(__name__)


class Setup(discore.Cog,
             name="setup",
             description="The bot setup, such as guild sync and top.gg autopost"):

    async def cog_load(self) -> None:
        if discore.config.analytic:
            _logger.info("[ACTIVITY] Starting custom activity")
            self.update_activity.start()
        else:
            _logger.warning("[ACTIVITY] Analytics disabled, activity disabled")

        if discore.config.topgg_token:
            _logger.info("[TOP.GG] Starting autopost")
            self.topgg_autopost.start()
        else:
            _logger.warning("[TOP.GG] `config.topgg_token` not set, autopost disabled")

    async def cog_unload(self):
        if self.update_activity.is_running():
            self.update_activity.cancel()

        if self.topgg_autopost.is_running():
            self.topgg_autopost.cancel()

    @discore.Cog.listener()
    async def on_login(self):
        utils.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        if discore.config.dev_guild and discore.config.auto_sync:
            await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
            _logger.info("Synced dev guild")
        else:
            _logger.warning("`config.dev_guild` not set, skipping dev commands sync")

        if not utils.is_sku():
            _logger.warning("`config.sku` not set, premium features unavailable")

    @discore.loop(hours=1)
    async def update_activity(self) -> None:
        """
        Update the bot activity every hour.

        :return: None
        """

        def format_count(n: int) -> str:
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f}".rstrip('0').rstrip('.') + 'M'
            if n >= 1_000:
                return f"{n / 1_000:.1f}".rstrip('0').rstrip('.') + 'k'
            return str(n)

        fixed_links_nb = len(Event.since('fixed_link', days=1))
        if fixed_links_nb == 0:
            return

        activity = discore.CustomActivity(f"Fixing {format_count(fixed_links_nb)} links per day")
        _logger.info(f"[ACTIVITY] {activity}")
        await self.bot.change_presence(activity=activity)

    @update_activity.before_loop
    async def before_update_activity(self) -> None:
        await self.bot.wait_until_ready()

    @discore.loop(hours=1)
    async def topgg_autopost(self) -> None:
        """
        Update the guild count on top.gg every hour.

        :return: None
        """

        try:
            async with utils.session.post(
                f"https://top.gg/api/bots/{self.bot.user.id}/stats",
                headers={'Authorization': discore.config.topgg_token, 'Content-Type': 'application/json'},
                data=json.dumps({'server_count': len(self.bot.guilds)}),
            ) as response:
                if response.status == 200:
                    _logger.info("[TOP.GG] Updated guild count")
                else:
                    _logger.error(f"[TOP.GG] Failed to update guild count, status code: {response.status}")
        except asyncio.TimeoutError:
            _logger.error("[TOP.GG] Timeout error while updating guild count")

    @topgg_autopost.before_loop
    async def before_topgg_autopost(self) -> None:
        await self.bot.wait_until_ready()
