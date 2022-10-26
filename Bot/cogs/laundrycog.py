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
                "w1" : {"type" : "washer", "loop" : self.w1_loop},
                "w2" : {"type" : "washer", "loop" : self.w2_loop},
                "d1" : {"type" : "drier", "loop" : self.d1_loop},
                "d2" : {"type" : "drier", "loop" : self.d2_loop}
            }
        
        for m in self.machines.keys():
            if machineStatus(m) > 1:
                self.machines[m]["loop"].start()
        
    @discord.slash_command()
    async def laundrystatus(self,ctx):
        outStr = f"{ctx.author.mention} the status of the laundry machines is:\n"
        for m in self.machines.keys():
            minutes = machineStatus(m)
            if minutes > 0:
                outStr += f" {m} has {minutes} min left.\n"
            else:
                outStr += f" {m} was run by {readMachine(m)['whoRan']} has been done for {-1*minutes} min.\n"
        await ctx.respond(outStr)
    
    @discord.slash_command()
    async def resetmachine(self, ctx, machine):
        setMachine(machine, ctx.author.mention, -1)
        await ctx.respond(f"Reset machine {machine}")
        if self.machines[machine]["loop"].is_running():
            self.machines[machine]["loop"].cancel()
    
    @discord.slash_command()
    async def machineloop(self,ctx,machine):
        await ctx.respond( self.machines[machine]["loop"].is_running() )


    async def machineMessage(self, ctx, machine, time):
        minutes = machineStatus(machine)

        if minutes > 0 or self.machines[machine]["loop"].is_running():
            await ctx.respond(ctx.author.mention + " the machine is in use by " + readMachine(machine)["whoRan"] + " and has " + str(minutes) + " min left.")
            return
        
        setMachine(machine, ctx.author.mention, time)
        await ctx.respond(ctx.author.mention + " started " + machine + " for " + str(time) + " minute(s).")
        self.machines[machine]["loop"].start()
        return

    @discord.slash_command()
    async def washer(self, ctx, num : Option(int, required = True), time : Option(int, default = wash_time_def)):
        machine = "w" + str(num)
        await self.machineMessage(ctx, machine, time)
    
    @discord.slash_command()
    async def drier(self, ctx, num : Option(int, required = True), time : Option(int, default = wash_time_def)):
        machine = "d" + str(num)
        await self.machineMessage(ctx,machine,time)

    @tasks.loop(minutes = max(machineStatus("w1"),1), count = 1)
    async def w1_loop(self):
        print(f"starting w1 loop for {machineStatus('w1')} min")

    @w1_loop.after_loop
    async def w1_after_loop(self):
        user = readMachine("w1")["whoRan"]

        channel = await self.bot.fetch_channel(SAM_CHANNEL_ID)
        await channel.send(f"{user} your laundry is done in washer 1")

    @tasks.loop(minutes = max(machineStatus("w2"),1), count = 1)
    async def w2_loop(self):
        print(f"starting w2 loop for {machineStatus('w2')} min")

    @w2_loop.after_loop
    async def w2_after_loop(self):
        user = readMachine("w2")["whoRan"]

        channel = await self.bot.fetch_channel(SAM_CHANNEL_ID)
        await channel.send(f"{user} your laundry is done in washer 2")

    @tasks.loop(minutes = max(machineStatus("d1"),1), count = 1)
    async def d1_loop(self):
        print(f"starting d1 loop for {machineStatus('d1')} min")

    @d1_loop.after_loop
    async def d1_after_loop(self):
        user = readMachine("d1")["whoRan"]

        channel = await self.bot.fetch_channel(SAM_CHANNEL_ID)
        await channel.send(f"{user} your laundry is done in drier 1")

    @tasks.loop(minutes = max(machineStatus("d2"),1), count = 1)
    async def d2_loop(self):
        print(f"starting d2 loop for {machineStatus('d2')} min")

    @d2_loop.after_loop
    async def d2_after_loop(self):
        user = readMachine("d2")["whoRan"]

        channel = await self.bot.fetch_channel(SAM_CHANNEL_ID)
        await channel.send(f"{user} your laundry is done in drier 2")


def setup(bot):
    bot.add_cog(LaundryCog(bot))