import asyncio
from typing import List
import discord_markdown_ast_parser as dmap
from discord_markdown_ast_parser.parser import NodeType
import logging

from database.models.Member import *
from database.models.Role import Role
from database.models.TextChannel import *
from database.models.Guild import *
from database.models.Event import *
from src.websites import *

import discore

__all__ = ('LinkFix',)

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


def filter_fixable_links(links: List[tuple[str, bool]], guild: Guild) -> List[WebsiteLink]:
    """
    Get only the fixable links from the list of links.

    :param links: the links to filter (url, spoiler)
    :param guild: the guild associated with the context
    :return: the fixable links, as WebsiteLink
    """

    return [link for url, spoiler in links if (link := get_website(guild, url, spoiler))]


def get_embeddable_links(nodes: List[dmap.Node], spoiler: bool = False) -> List[tuple[str, bool]]:
    """
    Parse and detects the embeddable links, ignoring links
    that are in a code block, in spoiler or ignored with <>

    :param nodes: the list of nodes to parse
    :param spoiler: if the nodes are in a spoiler
    :return: the list of detected links (url, spoiler)
    """

    links = []
    for node in nodes:
        match node.node_type:
            case NodeType.CODE_BLOCK | NodeType.CODE_INLINE:
                continue
            case NodeType.URL_WITH_PREVIEW_EMBEDDED | NodeType.URL_WITH_PREVIEW:
                links.append((node.url, spoiler))
            case NodeType.SPOILER:
                links += get_embeddable_links(node.children, spoiler=True)
            case _:
                links += get_embeddable_links(node.children, spoiler=spoiler)
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

    if discore.config.analytic:
        for link in links:
            Event.create({'name': 'link_' + link.id})

    async with message.channel.typing():
        fixed_links = [fixed_link for link in links if (fixed_link := await link.get_formatted_fixed_link())]

        if not fixed_links:
            return

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


class LinkFix(discore.Cog,
             name="link fix",
             description="Link fix events"):

    @discore.Cog.listener()
    async def on_message(self, message: discore.Message) -> None:
        """
        React to message creation events

        :param message: The message that was created
        :return: None
        """

        if (
                message.author == message.guild.me
                or not message.content
                or not message.channel
                or not message.guild
        ):
            return

        links = get_embeddable_links(dmap.parse(message.content))

        if not links:
            return

        guild = Guild.find_or_create(message.guild.id)

        links = filter_fixable_links(links, guild)

        if not links:
            return

        if not TextChannel.find_or_create(guild, message.channel.id).enabled:
            return

        if isinstance(message.author, discore.Member) and (
            not Member.find_or_create(message.author, guild).enabled
            or not all(r.enabled for r in Role.finds_or_creates(guild, [role.id for role in message.author.roles]))
        ):
            return

        if (
            message.webhook_id is not None and not bool(guild.webhooks)
        ):
            return

        await fix_embeds(message, guild, links)