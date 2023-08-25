import discord
from discord.ext import commands
from discord.commands import Option

from ..Duties_func import *
from constants import *

class DutiesCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # allows people to save name and pass name check
        if ctx.command.name == "savename":
            return True
        #Checking for saved name
        if not checkID(ctx.author.mention):
            await ctx.respond(f"{ctx.author.mention} save your name with '/savename LASTNAME'.")
            return False
    
        print(ctx.command.name)
        return True

    #async def cog_command_error(self, ctx, error):
    #    if isinstance(error, discord.errors.CheckFailure):
    #        await ctx.respond("You do not pass the checks for this command")
    #    print(error)

    @discord.slash_command(description = "Gives link to duties sheet.")
    async def duties(self, ctx):
        await ctx.respond(f'{ctx.author.mention} \nhttps://docs.google.com/spreadsheets/d/{SHEET_KEY}/edit?usp=sharing')

    def getDutyString(self, person):
        personID = getIDFromName(person)
        dutyInfo = getDutyInfo(person)
        if len(dutyInfo["duties"]) == 0:
            return "You have no duties this week " + personID + " !!"
            
        if len(dutyInfo["duties"]) == sum(dutyInfo["done"]):
            return "You finished your duties this week, " + personID + " thanks for keeping the lodge clean! :broom:"
        
        numDuties = len(dutyInfo["duties"])
        strOut = "" + personID + " you have " + str(numDuties) + " duties this week \n"
        for i in range(len(dutyInfo["duties"])):
            tempStr = "" + str(i+1) + " .   " + dutyInfo["duties"][i] + " " + dutyInfo["floors"][i] + " " + dutyInfo["rooms"][i]
            if dutyInfo["done"][i] == 1:
                tempStr = "~~" + tempStr + "~~"
            strOut += tempStr + "\n"
        return strOut

    @discord.slash_command(description = "Lists off duties of author or person listed.")
    async def whatsmyduty(self, ctx, person : Option(str, "Who's duties to check.", default = "")):
        atAuth = ctx.author.mention
        if person == "":
            person = getNameFromID(atAuth)
        strOut = self.getDutyString(person)
        await ctx.respond(strOut)
        return
    
    @discord.slash_command(description = "Gives descriptions of your duties.")
    async def describeduty(self, ctx, person : Option(str, "Who's duties to check.", default = "")):
        atAuth = ctx.author.mention
        if person == "":
            person = getNameFromID(atAuth)
        strOut = self.getDutyString(person)
        await ctx.respond(strOut)
        return

    @discord.slash_command(description = "Checks off all (or chosen) duties for author (or person).")
    async def didduty(self, ctx,
                    whos : Option(str, "Who's duty did you do?", default=""),
                    number : Option(int, "Duty number, only 1 at a time", default=-1)
                    ):
        
        if whos == "":
            whos = getNameFromID(ctx.author.mention)
        dutyInfo = getDutyInfo(whos)

        if number < 0:
            number = range(1,len(dutyInfo["coords"])+1)
        else: number = [number]

        if max(number) > len(dutyInfo["coords"]) or min(number) < 1:
            await ctx.respond(ctx.author.mention + " that duty index is out of range. Try again.")
            return

        await ctx.respond("Checked off your duties.")
        for i in number:
            checkOffDuty(dutyInfo["coords"][i-1])
        await ctx.channel.send(self.getDutyString(whos))
        return

    @discord.slash_command(description = "Saves author's last name for dutybot use.")
    async def savename(self, ctx, lastname : Option(str, "Your Lastname (capitalize first letter).", requried=True)):
        atAuth = ctx.author.mention
        
        # make sure nobody put LASTNAME as their name
        if lastname.lower() == "lastname":
            await ctx.respond( atAuth + " replace 'LASTNAME' with your last name you hooligan." )
            return
        
        # save name through NameHandler
        lastname = lastname[0].upper() + lastname[1:].lower()
        newData = {atAuth: lastname}
        updateName(newData)
        await ctx.respond( atAuth + ", saved your name as " + lastname + ".")
    
    @discord.slash_command()
    async def whois(self, ctx, name : Option(str, "either discord id or lastname", required = True)):
        atAuth = ctx.author.mention
        name = name.lower()
        if name[0] == "<":
            if not checkID(name):
                await ctx.respond( atAuth + " unknown user ID")
                return
            await ctx.respond(atAuth + f", the name is {getNameFromID(name)}")
            return
        
        name = name[0].upper() + name[1:]
        if not checkName(name):
            await ctx.respond(atAuth + " unkown name")
            return
        await ctx.respond(atAuth + f" discord id is {getIDFromName(name)}")
        return


    @discord.slash_command(description = "Shows percent of duties done.")
    async def percentdone(self, ctx):
        values = getSheetInfo('[Duties]').get_all_values()
        percent = int(values[len(values) - 1][0][:-3])
        print(percent)
        p10, p5, p1, p0 = "██", "▓", "▒", "░"
        perc = percent
        percBar = ""
        while perc >= 10:
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
        id = ctx.author.mention
        if not checkID(id):
            return False
        return getNameFromID(id) in ADMINS

    @discord.slash_command(description = "Admin Only - Pings all brothers who have not done their duty.")
    @commands.check(isAdmin)
    async def notdone(self, ctx):
        await ctx.respond("Getting names of brothers...")
        strOut = "These brothers have not done their duty\n"
        # get data once and feed it in for each name to reduce api calls
        data = getSheetInfo('[Duties]').get_all_values()
        for id in getNames().keys():
            name = getNameFromID(id)
            dutyInfo = getDutyInfo(name, data)
            # if number of duties is greater than number checked off
            if (len(dutyInfo["duties"]) > sum(dutyInfo["done"])):
                strOut += "\t" + id + "\n"
        await ctx.channel.send(strOut)

def setup(bot):
    bot.add_cog(DutiesCog(bot))