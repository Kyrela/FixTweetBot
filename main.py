import asyncio
import os
import discore

from src.utils import I18nTranslator

os.environ['DB_CONFIG_PATH'] = 'database/config.py'

intents = discore.Intents(guild_messages=True, message_content=True, guilds=True)

# A fixed link is built from what members post: it must never ping anyone but the member it replies to
allowed_mentions = discore.AllowedMentions(everyone=False, users=False, roles=False)

bot = discore.Bot(help_command=None, intents=intents, allowed_mentions=allowed_mentions)
asyncio.run(bot.tree.set_translator(I18nTranslator()))
bot.run()
