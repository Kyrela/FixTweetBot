from typing import List, Tuple
import re
import discord_markdown_ast_parser as dmap
from discord_markdown_ast_parser.parser import NodeType

from utils import *

import discore

__all__ = ('Events',)

twitter_regex = re.compile(
    r"https?://(?:www\.)?(?:twitter\.com|x\.com|nitter\.net)/([\w_]+)/status/(\d+)(/(?:photo|video)/\d)?/?(?:\?\S+)?")
instagram_regex = re.compile(
    r"https?://(?:www\.)?instagram.com/((?:p|reel)/([\w_-]+))/?(?:\?\S+)?")
tiktok_regex = re.compile(
    r"https?://(?:www\.)?tiktok.com/((?:t|@[\w_]+/video)/(?:[\w_]+))/?(?:\?\S+)?"
)


def get_embeddable_links(nodes: List[dmap.Node]) -> List[Tuple[re.Match[str], str]]:
    """
    Parse and detects the twitter/X embeddable links, ignoring links
    that are in a code block, in spoiler or ignored with <>

    :param nodes: the list of nodes to parse
    :return: the list of detected links
    """

    links = []
    for node in nodes:
        match node.node_type:
            case NodeType.CODE_BLOCK | NodeType.SPOILER | NodeType.CODE_INLINE:
                continue
            case NodeType.URL_WITH_PREVIEW_EMBEDDED | (
                    NodeType.URL_WITH_PREVIEW) if url := twitter_regex.fullmatch(node.url):
                links.append((url, 'twitter'))
            case NodeType.URL_WITH_PREVIEW_EMBEDDED | (
                    NodeType.URL_WITH_PREVIEW) if url := instagram_regex.fullmatch(node.url):
                links.append((url, 'instagram'))
            case NodeType.URL_WITH_PREVIEW_EMBEDDED | (
                    NodeType.URL_WITH_PREVIEW) if url := tiktok_regex.fullmatch(node.url):
                links.append((url, 'tiktok'))
            case _:
                links += get_embeddable_links(node.children)
    return links


async def fix_embeds(
        message: discore.Message, links: List[Tuple[re.Match[str], str]]) \
        -> None:
    """
    Remove the embeds from the message and send them as fixed ones

    :param message: the message to fix
    :param links: the matches to fix
    :return: None
    """

    permissions = message.channel.permissions_for(message.guild.me)

    if not permissions.send_messages or not permissions.embed_links:
        return

    fixed_links = []

    for link in links:
        link_type = link[1]
        content = link[0]
        if link_type == 'twitter':
            fixed_links.append(
                f"[Tweet • {content[1]}]({discore.config.fx_domain}/{content[1]}/status/{content[2]}{content[3] or ''})")
        elif link_type == 'tiktok':
            fixed_links.append(
                f"[TikTok]({discore.config.tk_domain}/{content[1]})")
        elif link_type == 'instagram':
            fixed_links.append(
                f"[Instagram]({discore.config.ig_domain}/{content[1]})")

    await message.reply("\n".join(fixed_links), mention_author=False)

    if permissions.manage_messages:
        try:
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

        if message.author.bot or not message.content or not message.channel \
                or not message.guild \
                or not is_fixtweet_enabled(message.guild.id, message.channel.id):
            return

        links = get_embeddable_links(dmap.parse(message.content))

        if not links:
            return

        await fix_embeds(message, links)

    @discore.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
