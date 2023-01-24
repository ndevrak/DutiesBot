import discord
from discord.ext import commands
from discord.ext import tasks
from discord.commands import Option

import random
from datetime import datetime as dt

from ..Duties_func import *
from constants import *

class TablesCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

        self.tablesloop.start()

    async def checkwipingtablestoday(ctx):
        return getNameFromID(ctx.author.mention) == getTableInfo()["cleaner"]
    
    async def isAdmin(ctx):
        return ctx.author.mention in ADMINS

    @discord.slash_command()
    @commands.check(checkwipingtablestoday)
    async def wipedtables(self, ctx):
        # TODO
        # check when someone uses this its their day to do tables
        # this requires some refactoring probably
            # message handler would need access to cron handler then
        atAuth = ctx.author.mention
        checkOffTable(getNameFromID(atAuth))
        await ctx.respond( atAuth + " checked it off, thanks for cleaning the tables!")
    
    @discord.slash_command()
    async def passtables(self, ctx):
        atAuth = ctx.author.mention
        lodgers = notCleanedLodgers()
        if len(lodgers) <= 1:
            ctx.respond( atAuth + " you are the last, you cannot pass on tables today." )
            return
        if not getNameFromID(atAuth) in lodgers:
            ctx.respond( atAuth + " you already wiped tables, no need to pass it.")
            return
        newCleaner = random.choice(lodgers)
        await ctx.respond( atAuth + " passed tables off to " + getIDFromName(newCleaner) + "." )
        updateTableCleaner(newCleaner)
        
    
    @discord.slash_command()
    @commands.check(isAdmin)
    async def redotables(self,ctx):
        lodgers = notCleanedLodgers()
        newCleaner = random.choice(lodgers)
        updateTableCleaner(newCleaner)
        await ctx.respond("" + getIDFromName(newCleaner) + " you are the new table wiper today.")
    
    @discord.slash_command()
    async def remindtables(self,ctx):
        info = getTableInfo()
        await ctx.respond(f"Hey { getIDFromName(info['cleaner']) } this is a reminder to wipe the tables.")

    def runtables(self):
        if not RUN_TABLES:
            return False
        hour = dt.now().strftime(CRON_TIME_FMT)
        day = dt.now().strftime(CRON_DATE_FMT)
        # if its a weekend
        if dt.now().weekday() > 4:
            return False
        # if its the standard tables times
        if int(hour) in TABLES_TIMES:
            return True
        # if its between standard times and tables have not run yet
        if int(hour) > int(TABLES_TIMES[0]) and int(hour) < int(TABLES_TIMES[1]):
            if getTableInfo()["date"] == day:
                return False
            return True
        # don't run
        return False

    @tasks.loop(hours=1)
    async def tablesloop(self):
        willruntables = self.runtables()
        print(f"tables loop will run : {willruntables}")
        if not willruntables:
            return

        if len(notCleanedLodgers()) == 0:
            resetTablesCol()

        # output message
        discordMessage = ''
        today = dt.now().strftime(CRON_DATE_FMT)
        # load in current data
        currentInfo = getTableInfo()
        if today == currentInfo["date"]:
            # tables already done today
            if loadTablesLodgers()[currentInfo["cleaner"]]:
                return
            # tables assigned today but not done yet
            person = currentInfo["cleaner"]
        else: 
            # get a new random person to clean
            person = random.choice(notCleanedLodgers())
            updateTableCleaner(person, today)
        # if person's name is not saved
        if not person in getNames().values():
            discordMessage += "It is " + person + "'s turn to wipe tables today, but their name is not saved.\nTell them to save their name using '.savename LASTNAME'."
        else:
            discordMessage += getIDFromName(person) + " it's your turn to wipe tables today."
        channel = await self.bot.fetch_channel(CLEANING_CHANNEL_ID)
        await channel.send(discordMessage)

def setup(bot):
    bot.add_cog(TablesCog(bot))