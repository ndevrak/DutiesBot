from secrets import *

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents = intents)

# we need to limit the guilds for testing purposes
# so other users wouldn't see the command that we're testing

guilds_ids = [1034573202791346267]

@bot.slash_command(description="Sends the bot's latency.", guilds_ids = guilds_ids) # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

print("STARTING BOT")
bot.run(samBotToken)
