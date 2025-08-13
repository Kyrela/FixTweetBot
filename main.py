import asyncio
import os
import discore

from src.utils import I18nTranslator

os.environ['DB_CONFIG_PATH'] = 'database/config.py'

intents = discore.Intents(guild_messages=True, message_content=True, guilds=True)

bot = discore.Bot(help_command=None, intents=intents)
asyncio.run(bot.tree.set_translator(I18nTranslator()))
bot.run()
