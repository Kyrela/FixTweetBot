"""
Intercepts messages, detects links that can be fixed, and sends the fixed links accordingly.
"""

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


def get_website(guild: Guild, url: str, spoiler: bool = False) -> WebsiteLink | None:
    """
    Get the website of the URL.

    :param guild: the guild associated with the context
    :param url: the URL to check
    :param spoiler: whether the link is in a spoiler
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
    :return: the fixable links as WebsiteLink
    """

    return [link for url, spoiler in links if (link := get_website(guild, url, spoiler))]


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


async def _build_link_error_data(links: List[WebsiteLink]) -> list[dict]:
    """Build error data for a list of links."""
    return [
        {
            'id': link.id,
            'fixed_link': (await link.get_fixed_url())[0],
            'original_url': link.url
        }
        for link in links
    ]


async def fix_embeds(
        message: discore.Message,
        guild: Guild,
        links: List[WebsiteLink]) -> None:
    """
    Edit the message if necessary, and send the fixed links.

    :param message: the message to fix
    :param guild: the guild associated with the context
    :param links: the WebsiteLink objects to fix

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

    async with Typing(channel):
        rendered_links: list[WebsiteLink] = []
        for link in links:
            if await link.render():
                rendered_links.append(link)

        if not rendered_links:
            return

        not_sent, messages = await send_fixed_links(rendered_links, guild, message)

    to_delete = []
    if messages:
        results = await asyncio.gather(*(wait_for_embed(msg) for msg in messages))
        to_delete = [msg for msg, has_embed in zip(messages, results) if not has_embed]

        if to_delete:
            links_in_deleted = [link for msg in to_delete for link in messages.get(msg, [])]
            err_data = {'links': await _build_link_error_data(links_in_deleted),
                        'messages': [{'message': repr(m), 'content': m.content} for m in to_delete],
                        'bot': message.author.bot}
            _logger.warning("Message(s) has no embed after waiting: %s", repr(err_data))
            await Event.buff_cr({'name': 'fixed_link_no_embed', 'data': err_data})
            await asyncio.gather(*(safe_send_coro(m.delete(), not_found=True, forbidden=True) for m in to_delete))
        for msg, msg_links in messages.items():
            if msg not in to_delete:
                for link in msg_links:
                    await Event.buff_cr({'name': 'fixed_link', 'data': {'id': link.id, 'bot': message.author.bot}})

    if not_sent:
        err_data = {'links': await _build_link_error_data(not_sent),
                    'messages_content': [str(link) for link in not_sent],
                    'bot': message.author.bot}
        await Event.buff_cr({'name': 'fixed_link_not_sent', 'data': err_data})
        _logger.warning("Message(s) failed to send: %s", repr(err_data))
    if messages and not to_delete and not not_sent:
        await edit_original_message(guild, message, permissions)


async def send_fixed_links(
        rendered_links: list[WebsiteLink],
        guild: Guild,
        original_message: discore.Message
) -> tuple[list[WebsiteLink], dict[discore.Message, list[WebsiteLink]]]:
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

    :param rendered_links: the rendered WebsiteLink objects to send
    :param guild: the guild associated with the context
    :param original_message: the original message associated with the context to reply to
    :return: a tuple containing the list of links that failed to be sent, and a dict of the messages sent with their corresponding links
    """

    messages_sent: dict[discore.Message, list[WebsiteLink]] = {}
    links_failed: list[WebsiteLink] = []

    grouped = group_items(rendered_links, 2000)

    for i, (message_content, links_in_group) in enumerate(grouped):
        if i == 0 and guild.reply_to_message:
            coro = discore.fallback_reply(original_message, message_content, silent=guild.reply_silently)
        else:
            coro = original_message.channel.send(message_content, silent=guild.reply_silently)
        
        sent, msg = await safe_send_coro(coro, invalid_form_body='Embed size exceeds maximum size', forbidden=True)
        if sent:
            messages_sent[msg] = links_in_group
        else:
            links_failed.extend(links_in_group)

    return links_failed, messages_sent


async def wait_for_embed(message: discore.Message) -> bool:
    """
    Wait for the message to have embeds.

    :param message: the message to wait for
    """

    if message.embeds:
        return True
    def check(before: discore.Message, after: discore.Message) -> bool:
        return after.id == message.id and len(after.embeds) > len(before.embeds)
    try:
        await discore.Bot.get().wait_for('message_edit', check=check, timeout=6)
    except asyncio.TimeoutError:
        return True if message.embeds else False
    return True


async def edit_original_message(guild: Guild, message: discore.Message, permissions: discore.Permissions) -> None:
    """
    Edit the original message according to the guild settings and permissions.

    :param guild: the guild associated with the context
    :param message: the message to edit
    :param permissions: the permissions of the bot in the channel the message was sent in
    """
    if not permissions.manage_messages or guild.original_message == OriginalMessage.NOTHING:
        return

    if guild.original_message == OriginalMessage.DELETE:
        await safe_send_coro(message.delete(), not_found=True, forbidden=True)
    else:
        await wait_for_embed(message)
        await safe_send_coro(message.edit(suppress=True), not_found=True, forbidden=True)
        await asyncio.sleep(1)
        if message.embeds:
            await safe_send_coro(message.edit(suppress=True), not_found=True, forbidden=True)


class LinkFix(discore.Cog,
             name="link fix",
             description="Link fix events"):

    @discore.Cog.listener()
    async def on_message(self, message: discore.Message) -> None:
        """
        React to message creation events

        :param message: The message that was created
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
