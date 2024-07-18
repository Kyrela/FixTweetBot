import os
import discore

os.environ['DB_CONFIG_PATH'] = 'database/config.py'

intents = discore.Intents(guild_messages=True, message_content=True, guilds=True, members=True)

discore.Bot(help_command=None, intents=intents).run()
