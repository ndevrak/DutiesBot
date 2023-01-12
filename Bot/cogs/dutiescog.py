import discord
from discord.ext import commands
from discord.commands import Option

from ..Duties_func import *
from constants import *

class DutiesCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    def cog_check(self, ctx):
        print(ctx.command.name)
        return True

    @discord.slash_command(description = "Gives link to duties sheet.")
    async def duties(self, ctx):
        await ctx.respond(f'{ctx.author.mention} \nhttps://docs.google.com/spreadsheets/d/1ea1RgZnsXDPV9tngNhNj4icn7Ujm4UphFhp5DcYICt4/edit?usp=sharing')

    @discord.slash_command(description = "Lists off duties of author or person listed.")
    async def whatsmyduty(self, ctx, person : Option(str, "Who's duties to check.", default = "")):
        if person == "":
            atAuth = ctx.author.mention
            if not checkID(atAuth):
                await ctx.respond(f"{ctx.author.mention} save your name with '/savename LASTNAME'.")
                return
        else:
            if not checkName(person):
                await ctx.respond(f"{person} your name is not saved, check for mispelling and make sure your name is saved.")
                return
            atAuth = getIDFromName(person)
        dutyInfo = getDutyInfo(getNameFromID(atAuth))

        if len(dutyInfo["duties"]) == 0:
            await ctx.respond("You have no duties this week " + atAuth + " !!")
            return
            
        if len(dutyInfo["duties"]) == sum(dutyInfo["done"]):
            await ctx.respond( "You finished your duties this week, " + atAuth + " thanks for keeping the lodge clean! :broom:")
            return
        
        numDuties = len(dutyInfo["duties"])
        strOut = "" + atAuth + " you have " + str(numDuties) + " duties this week \n"
        for i in range(len(dutyInfo["duties"])):
            tempStr = "" + str(i+1) + " .   " + dutyInfo["duties"][i] + " " + dutyInfo["floors"][i] + " " + dutyInfo["rooms"][i]
            if dutyInfo["done"][i] == 1:
                tempStr = "~~" + tempStr + "~~"
            strOut += tempStr + "\n"
        await ctx.respond(strOut)
        return

    @discord.slash_command(description = "Checks off all (or chosen) duties for author (or person).")
    async def didduty(self, 
                    ctx,
                    whos : Option(str, "Who's duty did you do?", default=""),
                    number : Option(int, "Duty number, only 1 at a time", default=-1)
                    ):
        if whos == "":
            if not checkID(ctx.author.mention):
                await ctx.respond(f"{ctx.author.mention} save your name with '/savename LASTNAME'.")
                return
            whos = getNameFromID(ctx.author.mention)
        if not checkName(whos):
            await ctx.respond(f"{whos} your name is not saved, check for mispelling and make sure your name is saved.")
            return
        dutyInfo = getDutyInfo(whos)

        if number < 0:
            number = range(len(dutyInfo["coords"]))
        else: number = [number]

        for i in number:
            try:
                checkOffDuty(dutyInfo["coords"][int(i)-1])
            except IndexError:
                await ctx.respond(ctx.author.mention + " that duty index is out of range. Try again.")
                return
        await ctx.respond("Checked off your duties.")
        await self.whatsmyduty(ctx, person = whos)

    @discord.slash_command(description = "Saves author's last name for dutybot use.")
    async def savename(self, ctx, lastname : Option(str, "Your Lastname (capitalize first letter).", requried=True)):
        atAuth = ctx.author.mention
        
        # make sure nobody put LASTNAME as their name
        if lastname == "LASTNAME":
            await ctx.respond( atAuth + " replace 'LASTNAME' with your last name you hooligan." )
            return
        
        # save name through NameHandler
        newData = {atAuth: lastname}
        updateName(newData)
        await ctx.respond( atAuth + ", saved your name as " + lastname + ".")

    @discord.slash_command(description = "Shows percent of duties done.")
    async def percentdone(self, ctx):
        values = getSheetInfo('Duties')[0]
        percent = int(values[len(values) - 1][0])
        p10, p5, p1, p0 = "██", "▓", "▒", "░"
        perc = percent
        percBar = ""
        while perc > 10:
            percBar += p10
            perc -= 10
        while perc > 5:
            percBar += p5
            perc -= 5
        if perc > 0:
            percBar += p1
        percBar += p0 * (20-len(percBar))

        await ctx.respond( "" + str(percent) + "% of the duties are done\n" + percBar)
    
    async def isAdmin(ctx):
        return ctx.author.mention in ADMINS

    @discord.slash_command(description = "Admin Only - Pings all brothers who have not done their duty.")
    @commands.check(isAdmin)
    async def notdone(self, ctx):
        strOut = "These brothers have not done their duty\n"
        # get data once and feed it in for each name to reduce api calls
        data = getSheetInfo("Duties")[0]
        for id in getNames().keys():
            name = getNameFromID(id)
            dutyInfo = getDutyInfo(name, data)
            # if number of duties is greater than number checked off
            if (len(dutyInfo["duties"]) > sum(dutyInfo["done"])):
                strOut += "\t" + id + "\n"
        await ctx.respond(strOut)

def setup(bot):
    bot.add_cog(DutiesCog(bot))