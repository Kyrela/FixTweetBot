import asyncio
from typing import List
import discord_markdown_ast_parser as dmap
from discord_markdown_ast_parser.parser import NodeType
import logging
import topgg

from database.models.Member import *
from database.models.Role import Role
from database.models.TextChannel import *
from database.models.Guild import *
from src.utils import is_sku
from src.websites import *

import discore

__all__ = ('Events',)

_logger = logging.getLogger(__name__)


def get_website(guild: Guild, url: str, spoiler: bool = True) -> Optional[WebsiteLink]:
    """
    Get the website of the URL.

    :param guild: the guild associated with the context
    :param url: the URL to check
    :param spoiler: if the URL is in a spoiler
    :return: the website of the URL
    """

    for website in websites:
        if link := website.if_valid(guild, url, spoiler):
            return link
    return None


def get_embeddable_links(nodes: List[dmap.Node], guild: Guild, spoiler: bool = False) -> List[WebsiteLink]:
    """
    Parse and detects the fixable links, ignoring links
    that are in a code block, in spoiler or ignored with <>

    :param nodes: the list of nodes to parse
    :param guild: the guild associated with the context
    :param spoiler: if the nodes are in a spoiler
    :return: the list of detected links
    """

    links = []
    for node in nodes:
        match node.node_type:
            case NodeType.CODE_BLOCK | NodeType.CODE_INLINE:
                continue
            case NodeType.URL_WITH_PREVIEW_EMBEDDED | NodeType.URL_WITH_PREVIEW \
                if link := get_website(guild, node.url, spoiler):
                links.append(link)
            case NodeType.SPOILER:
                links += get_embeddable_links(node.children, guild, spoiler=True)
            case _:
                links += get_embeddable_links(node.children, guild, spoiler=spoiler)
    return links


async def fix_embeds(
        message: discore.Message,
        guild: Guild,
        links: List[WebsiteLink]) -> None:
    """
    Edit the message if necessary, and send the fixed links.

    :param message: the message to fix
    :param guild: the guild associated with the context
    :param links: the matches to fix
    :return: None
    """

    permissions = message.channel.permissions_for(message.guild.me)

    if not permissions.send_messages or not permissions.embed_links:
        return

    fixed_links = [link.get_formatted_fixed_link() for link in links]

    if guild.reply:
        await discore.fallback_reply(message, "\n".join(fixed_links))
    else:
        await message.channel.send("\n".join(fixed_links))

    if permissions.manage_messages and guild.original_message != OriginalMessage.NOTHING:
        try:
            if guild.original_message == OriginalMessage.DELETE:
                await message.delete()
            else:
                await message.edit(suppress=True)
                await asyncio.sleep(2)
                await message.edit(suppress=True)
        except discore.NotFound:
            pass


class Events(discore.Cog,
             name="events",
             description="The bot events"):

    @discore.Cog.listener()
    async def on_message(self, message: discore.Message) -> None:
        """
        React to message creation events

        :param message: The message that was created
        :return: None
        """

        if (
                message.author.bot
                or not message.content
                or not message.channel
                or not message.guild
        ):
            return

        guild = Guild.find_or_create(message.guild.id)

        if (
                not TextChannel.find_or_create(guild, message.channel.id).enabled
                or not Member.find_or_create(guild, message.author.id).enabled
                or not (
                all(r.enabled for r in Role.finds_or_creates(guild, [role.id for role in message.author.roles]))
                if isinstance(message.author, discore.Member)
                else True)
        ):
            return

        links = get_embeddable_links(dmap.parse(message.content), guild)

        if not links:
            return

        await fix_embeds(message, guild, links)

    @discore.Cog.listener()
    async def on_ready(self):
        if discore.config.dev_guild:
            await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
            _logger.info("Synced dev guild")
        else:
            _logger.warning("`config.dev_guild` not set, skipping dev commands sync")

        if not is_sku():
            _logger.warning("`config.sku` not set, premium features unavailable")

        if not discore.config.topgg_token:
            _logger.warning("`config.topgg_token` not set, Top.gg autopost disabled")
            return

        autopost = (
            topgg.DBLClient(discore.config.topgg_token).set_data(self.bot).autopost()
            .on_success(lambda: _logger.info("Updated guild count on top.gg"))
            .on_error(lambda e: _logger.error(f"Failed to update guild count on top.gg: {e}")))

        @autopost.stats
        def get_stats(client: discore.Bot = topgg.data(discore.Bot)):
            return topgg.StatsWrapper(guild_count=len(client.guilds), shard_count=len(client.shards))

        autopost.start()
