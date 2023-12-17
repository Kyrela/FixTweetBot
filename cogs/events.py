from typing import List, Dict
import re
import discord_markdown_ast_parser as dmap

from utils import *

import discore

__all__ = ('Events',)

url_regex = re.compile(
    r"https?://(?:www\.)?(?:twitter\.com|x\.com|nitter\.net)/([\w_]+)/status/(\d+)(?:\?\S+)?")


def get_embeddable_links(nodes: List[Dict]) -> List[re.Match[str]]:
    """
    Parse and detects the twitter/X embeddable links, ignoring links
    that are in a code block, in spoiler or ignored with <>

    :param nodes: the list of nodes to parse
    :return: the list of detected links
    """

    links = []
    for node in nodes:
        match node['node_type']:
            case 'CODE_BLOCK' | 'SPOILER':
                continue
            case 'URL_WITH_PREVIEW_EMBEDDED' | 'URL_WITH_PREVIEW' if url := url_regex.fullmatch(node['url']):
                links.append(url)
            case _:
                if results := get_embeddable_links(node['children']):
                    links.append(*results)
    return links


async def fix_embeds(
        message: discore.Message, links: List[re.Match[str]]) \
        -> None:
    """
    Remove the embeds from the message and send them as fxtwitter ones

    :param message: the message to fix
    :param links: the matches to fix
    :return: None
    """

    permissions = message.channel.permissions_for(message.guild.me)

    if not permissions.send_messages or not permissions.embed_links:
        return

    if permissions.manage_messages:
        try:
            await message.edit(suppress=True)
        except discore.NotFound:
            return

    fixed_links = []

    for link in links:
        fixed_links.append(
            f"[Tweet • {link[1]}]({discore.config.fx_domain}/{link[1]}/status/{link[2]})")

    await message.channel.send("\n".join(fixed_links))


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

        links = get_embeddable_links(dmap.parse_to_dict(message.content))

        if not links:
            return

        await fix_embeds(message, links)

    @discore.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discore.Object(discore.config.dev_guild))
