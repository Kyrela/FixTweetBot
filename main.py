import asyncio
import os
import discord
from discord.ext import commands
import utils

os.environ['DB_CONFIG_PATH'] = 'database/config.py'

intents = discord.Intents(guild_messages=True, message_content=True, guilds=True)

utils.config_init()
utils.i18n_init()

bot = commands.AutoShardedBot(command_prefix=utils.config.prefix, help_command=None, intents=intents)

# TODO: set locale of command invocation


async def load_cogs():
    from cogs import commands as commands_cog, events, developer
    await bot.add_cog(commands_cog.Commands(bot))
    await bot.add_cog(events.Events(bot))
    await bot.add_cog(developer.Developer(bot))


asyncio.run(load_cogs())

bot.run(utils.config.token)
