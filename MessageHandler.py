import random

from SheetHandler import *
from NameHandler import *
from constants import *


class MessageHandler:
    def __init__(self, nameHandler, channels = ACTIVE_CHANNELS, ):
        # dictionary of message keys and methods to call if a message contains those keys
        # also has list of checks to run before executing actual method
        self.nh = nameHandler
        self.actions = {
                        ".duties" : {"funct" :self.duties, "checks": []},
                        ".whatsmyduty" : {"funct" : self.whatsmyduty, "checks": [self.nh.checkID]},
                        ".didmyduty" : {"funct" : self.didmyduty, "checks": [self.nh.checkID]},
                        ".savename" : {"funct" : self.savename, "checks": []},
                        ".percentdone" : {"funct" : self.percentdone, "checks": []},
                        ".notdone" : {"funct" : self.notdone, "checks": [self.sentByAdmin]},
                        ".sendasdutiesbot" : {"funct" : self.sendasdutiesbot, "checks" : [self.sentByAdmin]},
                        ".help duties" : {"funct" : self.helpduties, "checks" : []},
                        ".wiped tables" : {"funct" : self.wipedtables, "checks" : [self.nh.checkID]},
                        # test method
                        ".dutybot test 1" : {"funct" : self.dutybotTest1, "checks": [self.nh.checkID, self.sentByAdmin]}
                        }
        

    async def respond(self, message):
        # go through actions to find the one that matches message sent
        for key in self.actions.keys():
            if message.content.startswith(key):
                # log what action bot is doing
                print(key)

                # go through checks to make sure all permissions are good
                for check in self.actions[key]["checks"]:
                    if not check(self.atAuthor(message)):
                        await message.channel.send("You do not have permission to use this function.\n" + 
                                                    "If you have not saved your name use '.savename LASTNAME'\n" + 
                                                    "Otherwise contact lodge manager."
                                                    )
                        return
                
                # if name is saved when needed and is admin when needed, then execute the function
                await message.channel.send(await self.actions[key]["funct"](message))


    def sentByAdmin(self, atAuthor):
        return atAuthor in ADMINS

    def atAuthor(self, message):
        return '<@' + str(message.author.id) + '>'

    async def duties(self, message):
        return "" + self.atAuthor(message) + '\nhttps://docs.google.com/spreadsheets/d/1ea1RgZnsXDPV9tngNhNj4icn7Ujm4UphFhp5DcYICt4/edit?usp=sharing'

    async def whatsmyduty(self, message):
        atAuth = self.atAuthor(message)
        dutyInfo = getDutyInfo(self.nh.getNameFromID(atAuth))
        print(dutyInfo)
        
        #no duties
        if len(dutyInfo["duties"]) == 0:
            return "You have no duties this week " + atAuth + " !!"
        
        #all duties done
        if len(dutyInfo["duties"]) == sum(dutyInfo["done"]):
            return "You finished your duties this week, " + atAuth + " thanks for keeping the lodge clean!"
        
        #not all duties done
        numDuties = len(dutyInfo["duties"])
        strOut = "" + atAuth + " you have " + str(numDuties) + " duties this week \n"
        for i in range(len(dutyInfo["duties"])):
            tempStr = "" + str(i+1) + " .   " + dutyInfo["duties"][i] + " " + dutyInfo["floors"][i] + " " + dutyInfo["rooms"][i]
            if dutyInfo["done"][i] == 1:
                tempStr = "~~" + tempStr + "~~"
            strOut += tempStr + "\n"
        
        return strOut

    async def didmyduty(self, message):
        # format to get it to work needs to be ".didmyduty 2,3" no spaces
        atAuth = self.atAuthor(message)
        dutyInfo = getDutyInfo(self.nh.getNameFromID(atAuth))
        #print(dutyInfo)
        # check if a number follows the message
        try:
            index = message.content.split()[1].split(",")
        except IndexError:
            #default is to check off all duties
            index = range(len(dutyInfo["coords"]))

        for i in index:
            checkOffDuty(dutyInfo["coords"][int(i)-1])
        await message.add_reaction(SNAP_EMOTE)
        return "Checked off your duties.\n" + str(await self.whatsmyduty(message))

    async def savename(self, message):
        atAuth = self.atAuthor(message)
        # make sure that there is actually a name in messgae
        try:
            lastname = message.content.split()[1]
        except IndexError:
            return atAuth + " name not saved, make sure you added your lastname to the message."
        
        # make sure nobody put LASTNAME as their name
        if lastname == "LASTNAME":
            return atAuth + " replace 'LASTNAME' with your last name you hooligan."
        
        # save name through NameHandler
        newData = {atAuth: lastname}
        self.nh.updateName(newData)
        return atAuth + ", saved your name as " + lastname + "."    

    async def percentdone(self, message):
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

        return "" + str(percent) + "% of the duties are done\n" + percBar

    async def notdone(self, message):
        strOut = "These brothers have not done their duty\n"
        # get data once and feed it in for each name to reduce api calls
        data = getSheetInfo("Duties")[0]
        for id in self.ids_names.keys():
            name = self.nh.getNameFromID(id)
            dutyInfo = getDutyInfo(name, data)
            # if number of duties is greater than number checked off
            if (len(dutyInfo["duties"]) > sum(dutyInfo["done"])):
                strOut += "\t" + id + "\n"
        return strOut

    async def sendasdutiesbot(self, message):
        atAuth = self.atAuthor(message)
        # only sam can use this :)
        # this should be changed later but its funny
        if not(atAuth == "<@297509765347541016>"): 
            return "no fuck you"
        return message.content[17:]

    async def wipedtables(self, message):
        # TODO
        # check when someone uses this its their day to do tables
        # this requires some refactoring probably
            # message handler would need access to cron handler then
        atAuth = self.atAuthor(message)
        checkOffTable(self.nh.getNameFromID(atAuth))
        await message.add_reaction(SNAP_EMOTE)
        return atAuth + " checked it off, thanks for cleaning the tables!"

    async def helpduties(self, message):
        # TODO add descriptions to each method so .helpduties is actually useful
        outstr = "Here are the methods availible :\n"
        for key in self.actions.keys():
            outstr += "\t" + key + "\n"
        return outstr

    async def dutybotTest1(self, message):
        # test method
        print(getSheetInfo("Duties")[0][3][22])
        print(getSheetInfo("Duties")[0][16][22])
        return "tested"