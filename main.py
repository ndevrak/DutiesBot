## Outside imports -----------------------
# Importing discord to interact with discord
import discord
from discord.ext import tasks
# --- IMPORT Traceback Library --- used to get message in on_error
import traceback
# datetime for timeing
from datetime import datetime as dt

## Local imports -------------------------
from constants import *
import MessageHandler as MH
import CronHandler as CH
import NameHandler as NH


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

#### Structure of the Code ----------------
# constants.py is for storing constant values
    # update values to make sure that they match the real state of things

# Name handler keeps up the "ids_names.json"
    # this file associates brothers' last names with their discord ids

# Cron handler is used for timed and consistent messages
    # tables are run through this
    # if you want to set it up so it sends .notdone on wednesdays for example
        # then set it up through cron

# Message handler is for basic message repsonse
    # to add a message response make a method and add the message startswith key to actions

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

# On Error Handler
@client.event
async def on_error(event, *args, **kwargs):
    # Gets the message object and parses
    message = args[0]
    msgCausingError = message.content
    parsedMsgInfo = str(message).replace('>>', '\n\n').replace('>','\n\n').replace('<', '\n')
    # Gets error message from shell
    error = traceback.format_exc()
    # Sends message to #bot-error on Bot Test Server
    await client.get_channel(TEST_CHANNEL_ID).send('**EXCEPTION RAISED** ' 
                                                        +ADMINS[0] +
                                                        '\n\n`Message: ' +
                                                        msgCausingError + '`' +
                                                        parsedMsgInfo + '`' +
                                                        error + '`')
    if ('X-RateLimit-Limit' in parsedMsgInfo):
        await client.get_channel(TEST_CHANNEL_ID).send(
            '**DISCORD RATE LIMIT REACHED** ' + ADMINS[0])
    print('--- EXCEPTION RAISED\n--- sent to Bot Test Server')
    print('Event: ' + str(event))
    for item in args:
        print('args[' + str(args.index(item)) + ']: ' + str(item) + '\n')
    print('Error: ' + error)
    return


# Run Bot
client.run("ODE4NTYwOTk0MjA0MDU3NjEw.YEZ2VQ.LHd5zNfwJ6GGY8_NW1zRx7AAjgA")
