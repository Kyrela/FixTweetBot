from utils import create_db
import discore

create_db()

intents = discore.Intents(guild_messages=True, message_content=True, guilds=True)

discore.Bot(help_command=None, intents=intents).run()
