"""
Intercepts messages, detects links that can be fixed, and sends the fixed links accordingly.
"""

import asyncio
import re
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
from src.utils import *

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

    Remark:
      Discord API, when sending a message with links, first successfully sends
      the message, then tries to fetch the embeds. If one embed is too large,
      or every embed exceeds the limit together, it simply doesn't display
      it/them.
      However, if the embed has already been fetched and is still in Discord's
      cache (which lasts about ~1/2h), the embed length is checked when sending
      the message, and if it exceeds the limit, the message sending fails.

      Here, we wait a bit after sending the fixed links, and if no embed is
      present, we delete the sent message. And, only if all messages were sent
      and no message had to be deleted (no if we're not in situation 1 nor 2),
      we edit the original message.
    """

    channel = message.channel
    permissions = channel.permissions_for(message.guild.me)

    if (not (permissions.send_messages and permissions.embed_links)
        or (isinstance(channel, discore.Thread) and channel.locked)):
        return

    async with channel.typing():
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

        sent_everything, messages = await send_fixed_links(fixed_links, guild, message)

    if messages:
        tasks = [asyncio.create_task(wait_for_embed(msg)) for msg in messages]
        results = await asyncio.gather(*tasks)
        to_delete = [msg for msg, embedded in zip(messages, results) if not embedded]
        if to_delete:
            _logger.warning("Message(s) has no embed after waiting: %s", repr(to_delete))
            await asyncio.gather(*(m.delete() for m in to_delete))
        elif sent_everything:
            await edit_original_message(guild, message, permissions)


async def send_fixed_links(fixed_links: list[str], guild: Guild, original_message: discore.Message) -> tuple[bool, list[discore.Message]]:
    """
    Send the fixed links to the channel, according to the guild settings and its context

    Remark:
      Discord API, when sending a message with links, first successfully sends
      the message, then tries to fetch the embeds. If one embed is too large,
      or every embed exceeds the limit together, it simply doesn't display
      it/them.
      However, if the embed has already been fetched and is still in Discord's
      cache (which lasts about ~1/2h), the embed length is checked when sending
      the message, and if it exceeds the limit, the message sending fails.

      Here, if we are in the second case, we simply ignore the error, and
      return that not everything was sent.

    :param fixed_links: the fixed links to send, as strings
    :param guild: the guild associated with the context
    :param original_message: the original message associated with the context to reply to
    :return: whether all messages were sent without error
    """

    messages_contents = group_join(fixed_links, 2000)
    messages_sent: list[discore.Message] = []
    errored = False

    async def send_message(coro):
        nonlocal errored, messages_sent
        try:
            messages_sent.append(await coro)
        except discore.HTTPException as e:
            if e.code == 50035 and 'Embed size exceeds maximum size' in e.text:
                _logger.debug("Failed to send fixed links message due to embed size exceeding limit.")
                errored = True
            elif e.status == 429:
                _logger.warning(
                    f"Failed to send fixed links message due to rate limiting. Context: {entrypoint_context.get()!r}",
                    stack_info=True)
                await discore.Bot.get().get_channel(discore.config.log.channel).send(
                    f"Rate limit reached. Context: `{entrypoint_context.get()!r}`")
                errored = True
            else:
                raise

    if guild.reply_to_message and messages_contents:
        await send_message(discore.fallback_reply(original_message, messages_contents.pop(0), silent=guild.reply_silently))

    for message in messages_contents:
        await send_message(original_message.channel.send(message, silent=guild.reply_silently))

    return not errored, messages_sent


async def wait_for_embed(message: discore.Message) -> bool:
    """
    Wait for the message to have embeds.

    :param message: the message to wait for
    :return: None
    """

    if message.embeds:
        return True
    def check(before: discore.Message, after: discore.Message) -> bool:
        return after.id == message.id and len(after.embeds) > len(before.embeds)
    try:
        await discore.Bot.get().wait_for('message_edit', check=check, timeout=5)
    except asyncio.TimeoutError:
        return False
    return True


async def edit_original_message(guild: Guild, message: discore.Message, permissions: discore.Permissions) -> None:
    """
    Edit the original message according to the guild settings and permissions.

    :param guild: the guild associated with the context
    :param message: the message to edit
    :param permissions: the permissions of the bot in the channel the message was sent in
    :return: None
    """
    if not permissions.manage_messages or guild.original_message == OriginalMessage.NOTHING:
        return
    try:
        if guild.original_message == OriginalMessage.DELETE:
            await safe_send_coro(message.delete())
        else:
            await wait_for_embed(message)
            await safe_send_coro(message.edit(suppress=True))
    except (discore.NotFound, discore.Forbidden):
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

        entrypoint_context.set(f"event on_message {{message={message!r}}}")

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

        guild = Guild.find_or_create(message.guild)
        links = filter_fixable_links(urls, guild)

        if not links:
            return
        if any(
                re.search(rf"\b{re.escape(k)}\b", message.content) for k in guild.keywords
        ) != guild.keywords_use_allow_list:
            return
        if not TextChannel.find_get_enabled(message.channel, guild):
            return
        if isinstance(message.author, discore.Member) and (
            not Member.find_get_enabled(message.author, guild)
            or not (any if (guild and guild.roles_use_any_rule) else all)(Role.finds_get_enabled(message.author.roles, guild))
        ):
            return
        if message.webhook_id is not None and not bool(guild.webhooks):
            return

        await fix_embeds(message, guild, links)
