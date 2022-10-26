from secrets import *

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents = intents)

# we need to limit the guilds for testing purposes
# so other users wouldn't see the command that we're testing

guilds_ids = [1034573202791346267]

cogs_list = [
    'dutiescog',
    'tablescog',
    'laundrycog'
]

for cog in cogs_list:
    bot.load_extension(f'Bot.cogs.{cog}')

print("STARTING BOT")
bot.run(samBotToken)
