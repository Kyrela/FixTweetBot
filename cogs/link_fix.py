"""
Intercepts messages, detects links that can be fixed, and sends the fixed links accordingly.
"""

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


def get_website(guild: Guild, url: str) -> Optional[WebsiteLink]:
    """
    Get the website of the URL.

    :param guild: the guild associated with the context
    :param url: the URL to check
    :return: the website of the URL
    """

    for website in websites:
        if link := website.if_valid(guild, url):
            return link
    return None


def filter_fixable_links(links: List[tuple[str, bool]], guild: Guild) -> List[tuple[WebsiteLink, bool]]:
    """
    Get only the fixable links from the list of links.

    :param links: the links to filter (url, spoiler)
    :param guild: the guild associated with the context
    :return: the fixable links, as WebsiteLink, along with their spoiler status
    """

    return [(link, spoiler) for url, spoiler in links if (link := get_website(guild, url))]


def get_embeddable_urls(nodes: List[dmap.Node], spoiler: bool = False) -> List[tuple[str, bool]]:
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
                links += get_embeddable_urls(node.children, spoiler=True)
            case _:
                links += get_embeddable_urls(node.children, spoiler=spoiler)
    return links


async def fix_embeds(
        message: discore.Message,
        guild: Guild,
        links: List[tuple[WebsiteLink, bool]]) -> None:
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

    async with message.channel.typing():
        fixed_links = []
        for link, spoiler in links:
            fixed_link = await link.render()
            if not fixed_link:
                continue
            if spoiler:
                fixed_link =  f"||{fixed_link} ||"
            fixed_links.append(fixed_link)
            if discore.config.analytic:
                Event.create({'name': 'link_' + link.id})

        if not fixed_links:
            return

        await send_fixed_links(fixed_links, guild, message)

        await edit_original_message(guild, message, permissions)


async def send_fixed_links(fixed_links: list[str], guild: Guild, original_message: discore.Message) -> None:
    """
    Send the fixed links to the channel, according to the guild settings and its context

    :param fixed_links: the fixed links to send, as strings
    :param guild: the guild associated with the context
    :param original_message: the original message associated with the context to reply to
    :return: None
    """

    messages = []
    for line in fixed_links:
        if not messages:
            messages.append(line)
            continue

        if len(messages[-1]) + len(line) + 1 > 2000:
            messages.append(line)
            continue

        messages[-1] += f"\n{line}"

    if guild.reply:
        await discore.fallback_reply(original_message, messages.pop(0))

    for message in messages:
        await original_message.channel.send(message)


async def edit_original_message(guild: Guild, message: discore.Message, permissions: discore.Permissions) -> None:
    """
    Edit the original message according to the guild settings and permissions.

    :param guild: the guild associated with the context
    :param message: the message to edit
    :param permissions: the permissions of the bot in the channel the message was sent in
    :return: None
    """
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
                or message.is_system()
        ):
            return

        urls = get_embeddable_urls(dmap.parse(message.content))

        if not urls:
            return

        guild = Guild.find_or_create(message.guild.id)
        links = filter_fixable_links(urls, guild)

        if not links:
            return
        if not TextChannel.find_or_create(guild, message.channel.id).enabled:
            return
        if isinstance(message.author, discore.Member) and (
            not Member.find_or_create(message.author, guild).enabled
            or not all(r.enabled for r in Role.finds_or_creates(guild, [role.id for role in message.author.roles]))
        ):
            return
        if message.webhook_id is not None and not bool(guild.webhooks):
            return

        await fix_embeds(message, guild, links)