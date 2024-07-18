from typing import List, Type
import re
import discord_markdown_ast_parser as dmap
from discord_markdown_ast_parser.parser import NodeType

from database.models.Member import *
from database.models.TextChannel import *
from database.models.Guild import *
from src.websites import *

import discore

__all__ = ('Events',)

url_regex = re.compile(
    r"https?://(?:www\.)?(?:twitter\.com|x\.com|nitter\.net)/([\w_]+)/status/(\d+)(/(?:photo|video)/\d)?/?(?:\?\S+)?")

websites: list[Type[WebsiteLink]] = [
    TwitterLink,
    InstagramLink,
    CustomLink
]


def get_website(guild: Guild, url: str, spoiler: bool = True) -> Optional[WebsiteLink]:
    """
    Get the website of the URL.

    :param guild: the guild associated with the context
    :param url: the URL to check
    :param spoiler: if the URL is in a spoiler
    :return: the website of the URL
    """

    for website in filter(lambda w: w.is_enabled(guild), websites):
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

    fixed_links = [link.fixed_link for link in links]

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
        ):
            return

        links = get_embeddable_links(dmap.parse(message.content), guild)

        if not links:
            return

        await fix_embeds(message, guild, links)

    @discore.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
