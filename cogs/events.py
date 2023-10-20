from typing import Iterator
import re
from utils import *

import discore

__all__ = ('Events',)

pattern = re.compile(
    r"<?https?://(?:www\.)?(?:twitter|x)\.com/([\w_]+/status/\d+)(?:\?\S+)?>?")


async def fix_embeds(
        message: discore.Message, matches: Iterator[re.Match[str]]) \
        -> None:
    """
    Remove the embeds from the message and send them as fxtwitter ones

    :param message: the message to fix
    :param matches: the matches to fix
    :return: None
    """

    permissions = message.channel.permissions_for(message.guild.me)

    if not permissions.send_messages or not permissions.embed_links:
        return

    if permissions.manage_messages:
        await message.edit(suppress=True)

    for match in matches:
        if match[0][0] == "<" and match[0][-1] == ">":
            continue
        await message.channel.send(f"{discore.config.fx_domain}/{match[1]}")


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
                or not message.guild or not is_fixtweet_enabled(message.guild.id):
            return

        matches = tuple(filter(
            lambda match: match[0][0] != "<" or match[0][-1] != ">",
            pattern.finditer(message.content)))
        if not matches:
            return

        await fix_embeds(message, matches)

    @discore.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync(guild=discore.Object(discore.config.guild))
