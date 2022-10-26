import discord
from discord.ext import commands
from discord.ext import tasks
from discord.commands import Option

from datetime import datetime as dt

from ..Laundry_func import *
from constants import *

class LaundryCog(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot

        self.machines = {
                "w1" : {"name" : "washer 1", "deftime" : wash_time_def},
                "w2" : {"name" : "washer 2", "deftime" : wash_time_def},
                "d1" : {"name" : "drier 1", "deftime" : dry_time_def},
                "d2" : {"name" : "drier 2", "deftime" : dry_time_def}
            }
        
        self.laundry_loop.start()
        
    @discord.slash_command()
    async def laundrystatus(self,ctx):
        outStr = f"{ctx.author.mention} the status of the laundry machines is:\n"
        for m in self.machines.keys():
            minutes = machineStatus(m)
            if minutes >= 0:
                outStr += f" {m} has {minutes} min left.\n"
            else:
                minutes = "many" if abs(minutes) > 300 else str(-1*minutes)
                outStr += f" {m} was run by {readMachine(m)['whoRan']} has been done for {minutes} min.\n"
        await ctx.respond(outStr)
    
    @discord.slash_command()
    async def resetmachine(self, ctx, machine):
        setMachine(machine, ctx.author.mention, -1)
        await ctx.respond(f"Reset machine {machine}")


    async def machineMessage(self, ctx, machine, time):
        minutes = machineStatus(machine)

        if minutes >= 0:
            await ctx.respond(ctx.author.mention + " the machine is in use by " + readMachine(machine)["whoRan"] + " and has " + str(minutes) + " min left.")
            return
        
        setMachine(machine, ctx.author.mention, time)
        await ctx.respond(ctx.author.mention + " started " + machine + " for " + str(time) + " minute(s).")
        return

    @discord.slash_command()
    async def washer(self, ctx, num : Option(int, required = True), time : Option(int, default = wash_time_def)):
        machine = "w" + str(num)
        await self.machineMessage(ctx, machine, time)
    
    @discord.slash_command()
    async def drier(self, ctx, num : Option(int, required = True), time : Option(int, default = wash_time_def)):
        machine = "d" + str(num)
        await self.machineMessage(ctx,machine,time)

    @tasks.loop(minutes = 1)
    async def laundry_loop(self):
        for m in self.machines:
            min = machineStatus(m)
            print(f"{m} has {min} left")
            if min == -1:
                channel = await self.bot.fetch_channel(LAUNDRY_CHANNEL_ID)
                await channel.send(f"{readMachine(m)['whoRan']} your laundry in {m} is done!")


def setup(bot):
    bot.add_cog(LaundryCog(bot))