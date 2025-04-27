import logging
import topgg

from src.utils import is_sku
from database.models.Event import *

import discore

__all__ = ('Setup',)

_logger = logging.getLogger(__name__)


class Setup(discore.Cog,
             name="setup",
             description="The bot setup, such as guild sync and top.gg autopost"):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.autopost = None
        if discore.config.topgg_token:
            self.autopost = (
                topgg.DBLClient(discore.config.topgg_token).set_data(self.bot).autopost()
                .on_success(lambda: _logger.info("Updated guild count on top.gg"))
                .on_error(lambda e: _logger.error(f"Failed to update guild count on top.gg: {e}")))

            @self.autopost.stats
            def get_stats(client: discore.Bot = topgg.data(discore.Bot)):
                return topgg.StatsWrapper(guild_count=len(client.guilds), shard_count=len(client.shards))

    @discore.Cog.listener()
    async def on_login(self):
        if discore.config.dev_guild:
            await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
            _logger.info("Synced dev guild")
        else:
            _logger.warning("`config.dev_guild` not set, skipping dev commands sync")

        if not is_sku():
            _logger.warning("`config.sku` not set, premium features unavailable")

    @discore.Cog.listener()
    async def on_connect(self):
        if self.autopost and not self.autopost.is_running:
            _logger.info("Starting top.gg autopost")
            self.autopost.start()
        else:
            _logger.warning("`config.topgg_token` not set, Top.gg autopost disabled")

        if discore.config.analytic and not self.update_status.is_running():
            _logger.info("Starting custom status")
            self.update_status.start()
        else:
            _logger.warning("Analytics disabled, status disabled")

    @discore.loop(hours=1)
    async def update_status(self):
        """
        Update the bot status every hour.

        :return: None
        """

        fixed_links_nb = len(Event.since())
        if fixed_links_nb == 0:
            return

        status = discore.CustomActivity(f"Fixing {fixed_links_nb} links per day")
        _logger.info(f"[STATE] : {status}")
        await self.bot.change_presence(activity=status)
