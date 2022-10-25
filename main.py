## Outside imports -----------------------
# Importing discord to interact with discord
import discord
from discord.ext import tasks
from discord.ext import commands
# --- IMPORT Traceback Library --- used to get message in on_error
import traceback
# datetime for timeing
from datetime import datetime as dt

## Local imports -------------------------
from constants import *
from secrets import *
import Duties_func.MessageHandler as MH
import Duties_func.CronHandler as CH
import Duties_func.NameHandler as NH

intents = discord.Intents.default()
intents.message_content = True

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents = intents)

# Create handler objects to cover different tasks
nh = NH.NameHandler()
ch = CH.CronHandler(client, nh)
mh = MH.MessageHandler(nh)

# Set up discord bot and start tasks
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name='you clean 🧼🧼🧼'))
    print(f'We have logged in as {client.user}')
    
    hourlyCron.start()

# task loop
@tasks.loop(hours=1)
async def hourlyCron():
    print("hourly cron ran on : " + dt.now().strftime("%A %H:%M"))
    await ch.cron()

# Message Handler
@client.event
async def on_message(message):
    #ignores messages sent by the bot
    if message.author == client.user:
        return
    
    await mh.respond(message)


# Run Bot
print("STARTING BOT")
bot.run(samBotToken)
