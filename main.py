from secrets import *

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents = intents)   

cogs_list = [
    'dutiescog',
    'laundrycog'
]

for cog in cogs_list:
    bot.load_extension(f'Bot.cogs.{cog}')

@bot.check
async def global_check(ctx):
    return True

@bot.event
async def on_connect():
    print("BOT CONNECTED")

print("STARTING BOT")
print("............")
bot.run(samBotToken)
