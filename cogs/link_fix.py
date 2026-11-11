"""
Intercepts messages, detects links that can be fixed, and sends the fixed links accordingly.
"""

import re
from dataclasses import dataclass, field
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


@dataclass
class Fix:
    """The fixed messages sent for a message, kept to be able to delete them afterwards."""

    original_id: int
    guild_id: int
    author_id: int
    messages: list[discore.Message] = field(default_factory=list)
    original_deleted: bool = False


# The fixes, by the id of their original message and of each of their fixed messages.
# They are kept in memory and capped: the links fixed before a restart (or about 10 000 fixes ago) can't be removed
# automatically anymore. They would have to be stored in the database if it ever matters.
MAX_TRACKED_MESSAGES = 20_000
tracked_fixes: dict[int, Fix] = {}

# The reaction that deletes a fixed message
DELETE_EMOJI = '❌'


def track_original(original_message: discore.Message) -> Fix:
    """
    Remember a message that is about to be fixed, to know if it gets deleted from then on.

    :param original_message: the message that is about to be fixed
    :return: the fix of the message
    """

    fix = tracked_fixes.setdefault(
        original_message.id, Fix(original_message.id, original_message.guild.id, original_message.author.id))
    while len(tracked_fixes) > MAX_TRACKED_MESSAGES:
        del tracked_fixes[next(iter(tracked_fixes))]
    return fix


def track_fix(fix: Fix, message: discore.Message) -> None:
    """
    Remember a fixed message, to be able to delete it afterwards.

    :param fix: the fix the message belongs to
    :param message: the message containing the fixed links
    """

    fix.messages.append(message)
    tracked_fixes[message.id] = fix


async def on_message_deleted(message_id: int) -> None:
    """
    Delete the fixed messages of a deleted message, if the guild asks for it.

    :param message_id: the id of the deleted message
    """

    fix = tracked_fixes.pop(message_id, None)
    if fix is None:
        return
    if message_id != fix.original_id:
        # A fixed message has been deleted, not the original one
        fix.messages[:] = [message for message in fix.messages if message.id != message_id]
        return
    fix.original_deleted = True
    if Guild.find(fix.guild_id).delete_with_original:
        messages = list(fix.messages)
        fix.messages.clear()
        for message in messages:
            tracked_fixes.pop(message.id, None)
        await asyncio.gather(*(safe_send_coro(m.delete(), not_found=True, forbidden=True) for m in messages))


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

    return [link for url, spoiler in links if (link := get_website(guild, url, spoiler)) is not None]


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

async def _format_link_data(link: WebsiteLink, original_message: discore.Message, message: discore.Message | str | None = None, include_sensitive: bool = False) -> dict:
    """
    Format the data of a link for logging or analytics purposes.

    :param link: the WebsiteLink object to format
    :param original_message: the original message associated with the context
    :param message: the message associated with the fixed link, if any (can be a string or a discore.Message)
    :param include_sensitive: whether to include sensitive data such as the message content or the fixed link URL
    :return: the formatted data as a dict
    """
    data: dict = {
        'link': {'id': link.id},
        'bot': original_message.author.bot
    }
    if not include_sensitive:
        return data

    if message is not None:
        data['message'] = {}
        if isinstance(message, discore.Message):
            data['message']['repr'] = repr(message)
            message = message.content
        data['message']['content'] = message

    data['link']['fixed_link'] = (await link.get_fixed_url())[0]
    data['link']['original_url'] = link.url
    return data


async def fix_embeds(
        original_message: discore.Message,
        guild: Guild,
        links: List[WebsiteLink]) -> None:
    """
    Edit the message if necessary, and send the fixed links.

    :param original_message: the message to fix
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

    channel = original_message.channel
    permissions = channel.permissions_for(original_message.guild.me)

    if (not (permissions.send_messages and permissions.embed_links)
        or (isinstance(channel, discore.Thread) and (channel.locked or channel.archived))):
        return

    # Registered before anything is sent, as the original message can be deleted while its links are being fixed
    fix = track_original(original_message) if guild.delete_with_original or guild.delete_on_reaction else None

    async def render_and_send() -> tuple[list[tuple[str, list[WebsiteLink]]], dict[discore.Message, list[WebsiteLink]]]:
        rendered_links = [link for link in links if await link.render()]
        if not rendered_links:
            return [], {}
        return await send_fixed_links(rendered_links, guild, original_message, fix)

    if guild.reply_as_original_author_replica:
        not_sent, messages = await render_and_send()
    else:
        async with Typing(channel):
            not_sent, messages = await render_and_send()

    if fix is not None and not fix.messages:
        tracked_fixes.pop(original_message.id, None)

    to_delete = []
    to_react = []
    if messages:
        results = await asyncio.gather(*(wait_for_embed(msg) for msg in messages))
        # A fixed message deleted in the meantime (along with its original message, or on a reaction) didn't fail
        to_delete = [
            msg for msg, has_embed in zip(messages, results)
            if not has_embed and not (fix is not None and msg not in fix.messages)]

        if to_delete:
            err_data = [
                {'name': 'fixed_link_no_embed', 'data': await _format_link_data(link, original_message, msg, include_sensitive=True)}
                for msg in to_delete for link in messages.get(msg, [])]
            _logger.warning("Message(s) has no embed after waiting: %s", repr(err_data))
            await Event.buff_cr(*err_data)
            await asyncio.gather(*(safe_send_coro(m.delete(), not_found=True, forbidden=True) for m in to_delete))
        for msg, msg_links in messages.items():
            if msg not in to_delete:
                await Event.buff_cr(*[
                    {'name': 'fixed_link', 'data': await _format_link_data(link, original_message)}
                    for link in msg_links])

        if (guild.delete_on_reaction and guild.add_delete_reaction
                and permissions.add_reactions and permissions.read_message_history):
            # Added once the fixed messages are known to stay, so that the reaction only has to be clicked
            to_react = [msg for msg in fix.messages if msg not in to_delete]

    if not_sent:
        err_data = [
            {'name': 'fixed_link_not_sent', 'data': await _format_link_data(link, original_message, msg_content, include_sensitive=True)}
            for msg_content, links in not_sent for link in links]
        _logger.warning("Message(s) failed to send: %s", repr(err_data))
        await Event.buff_cr(*err_data)
    tasks = [safe_send_coro(msg.add_reaction(DELETE_EMOJI), not_found=True, forbidden=True) for msg in to_react]
    if messages and not to_delete and not not_sent:
        tasks.append(edit_original_message(guild, original_message, permissions))
    await asyncio.gather(*tasks)


async def send_fixed_links(
        rendered_links: list[WebsiteLink],
        guild: Guild,
        original_message: discore.Message,
        fix: Fix | None = None
) -> tuple[list[tuple[str, list[WebsiteLink]]], dict[discore.Message, list[WebsiteLink]]]:
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
    :param fix: the fix of the original message, if its fixed messages have to be remembered
    :return: a tuple containing the list of links that failed to be sent, and a dict of the messages sent with their corresponding links
    """

    def abandoned() -> bool:
        """Whether the original message was deleted meanwhile, and its fixed links have to go with it"""
        return fix is not None and fix.original_deleted and guild.delete_with_original

    messages_sent: dict[discore.Message, list[WebsiteLink]] = {}
    links_failed: list[tuple[str, list[WebsiteLink]]] = []

    grouped = group_items(rendered_links, 2000)
    use_original_author_replica = guild.reply_as_original_author_replica
    webhook = await get_or_create_webhook(original_message.channel) if use_original_author_replica else None

    for i, (message_content, links_in_group) in enumerate(grouped):
        if abandoned():
            break
        if webhook is not None:
            coro = webhook_send(webhook, original_message, message_content, guild.reply_silently)
        elif i == 0 and guild.reply_to_message:
            coro = discore.fallback_reply(original_message, message_content, silent=guild.reply_silently)
        else:
            coro = original_message.channel.send(message_content, silent=guild.reply_silently)

        sent, msg = await safe_send_coro(coro, invalid_form_body='Embed size exceeds maximum size', forbidden=True)
        if sent and msg:
            if abandoned():
                await safe_send_coro(msg.delete(), not_found=True, forbidden=True)
                break
            messages_sent[msg] = links_in_group
            if fix is not None:
                track_fix(fix, msg)
        else:
            links_failed.append((message_content, links_in_group))

    return links_failed, messages_sent


async def get_or_create_webhook(channel: GuildMessageableChannel) -> discore.Webhook | None:
    """
    Get or create the webhook used to send messages as the original author.

    :param channel: the channel to send the fixed links to
    :return: the webhook to use, if available
    """

    webhook_channel = channel.parent if isinstance(channel, discore.Thread) else channel
    if webhook_channel is None:
        return None

    if not hasattr(webhook_channel, 'webhooks') or not hasattr(webhook_channel, 'create_webhook'):
        return None

    if not webhook_channel.permissions_for(channel.guild.me).manage_webhooks:
        return None

    success, webhooks = await safe_send_coro(webhook_channel.webhooks(), forbidden=True)
    if not success:
        return None
    bot = discore.Bot.get()
    webhook = next((
        w for w in webhooks
        if getattr(w.user, 'id', None) == bot.user.id
    ), None)
    if webhook is not None:
        return webhook
    success, webhook = await safe_send_coro(webhook_channel.create_webhook(name=bot.user.display_name), forbidden=True)
    return webhook if success else None


async def webhook_send(
        webhook: discore.Webhook,
        original_message: discore.Message,
        content: str,
        silent: bool
) -> discore.Message:
    """
    Send a fixed link using the original author's display name and avatar.

    :param webhook: the webhook to use
    :param original_message: the message associated with the context to reply to
    :param content: the content to send
    :param silent: whether to send the message silently
    :return: the message created by the webhook
    """

    kwargs = {
        'content': content,
        'username': original_message.author.display_name,
        'avatar_url': original_message.author.display_avatar.url,
        'silent': silent,
        'wait': True
    }
    if isinstance(original_message.channel, discore.Thread):
        kwargs['thread'] = original_message.channel
    return await webhook.send(**kwargs)


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
        # Deleting the original message ourselves must not delete its fixed links
        tracked_fixes.pop(message.id, None)
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

    @discore.Cog.listener()
    async def on_raw_message_delete(self, payload: discore.RawMessageDeleteEvent) -> None:
        if payload.message_id in tracked_fixes:
            entrypoint_context.set(f"event on_raw_message_delete {{payload={payload!r}}}")
            await on_message_deleted(payload.message_id)

    @discore.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: discore.RawBulkMessageDeleteEvent) -> None:
        for message_id in payload.message_ids & tracked_fixes.keys():
            entrypoint_context.set(f"event on_raw_bulk_message_delete {{payload={payload!r}}}")
            await on_message_deleted(message_id)

    @discore.Cog.listener()
    async def on_raw_reaction_add(self, payload: discore.RawReactionActionEvent) -> None:
        """
        Delete a fixed message when its original author, or a member who can manage messages, reacts to it with ❌,
        if the guild asks for it

        :param payload: The reaction that was added
        """

        fix = tracked_fixes.get(payload.message_id)
        if fix is None or payload.emoji.name != DELETE_EMOJI or payload.message_id == fix.original_id:
            return
        if payload.member is None or payload.member.bot:
            return
        entrypoint_context.set(f"event on_raw_reaction_add {{payload={payload!r}}}")
        message = next((m for m in fix.messages if m.id == payload.message_id), None)
        if message is None:
            return
        channel = self.bot.get_channel(payload.channel_id)
        if payload.user_id != fix.author_id and not (
                channel and channel.permissions_for(payload.member).manage_messages):
            return
        if not Guild.find(fix.guild_id).delete_on_reaction:
            return
        await safe_send_coro(message.delete(), not_found=True, forbidden=True)
