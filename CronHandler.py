from datetime import datetime as dt
import json
import random

from constants import *
from SheetHandler import *

class CronHandler:
    def __init__(self, client, nameHandler, json_path = "cron.json"):
        # actiosn is the crons
        # TODO change key to not be a method
            # it works but its kinda clunky
        self.actions = {
                        self.tableCron : {"times" : TABLES_TIMES , "run" : RUN_TABLES, "checks" : []},
                        self.testCron : {"times" : ["10","11"], "run" : True, "checks" : []}
                        }
        self.cron_path = json_path
        self.client = client
        self.nh = nameHandler
    
    async def cron(self):
        hour = dt.now().strftime(CRON_TIME_FMT)
        day = dt.now().strftime(CRON_DATE_FMT)

        # iterate through actions
        for key in self.actions.keys():
            # if action is set to run
            if self.actions[key]["run"]:
                # if action time lines up with now
                if hour in self.actions[key]["times"]:
                    # if passes all checks
                    if self.checkChecks(key):
                        # do the action
                        await key()

    def checkChecks(self, key):
        for check in self.actions[key]["checks"]:
            if not check():
                return False
        return True

    async def tableCron(self):
        # if everyone has cleaned, reset the table
        if len(notCleanedLodgers()) == 0:
            resetTablesCol()

        # output message
        discordMessage = ''
        day = dt.now().strftime(CRON_DATE_FMT)
        # load in current data
        with open(self.cron_path, 'r') as f:
            data = json.load(f)["tables"]
        person = ""
        if day in data.keys():
            # tables already done today
            if loadTablesLodgers()[data[day]["cleaner"]]:
                return
            # tables assigned today but not done yet
            person = data[day]["cleaner"]
        else: 
            # get a new random person to clean
            person = random.choice(notCleanedLodgers())
            # add this day and person to the json
            data[day] = {"cleaner" : person}
            with open(self.cron_path, 'r') as f:
                alldata = json.load(f)
            alldata["tables"] = data
            with open(self.cron_path, 'w') as f:
                json.dump(alldata, f)
        # if person's name is not saved
        if not person in self.nh.getNames().values():
            discordMessage += "It is " + person + "'s turn to wipe tables today, but their name is not saved.\nTell them to save their name using '.savename LASTNAME'."
        else:
            discordMessage += self.nh.getIDFromName(person) + " it's your turn to wipe tables today."
        await self.client.get_channel(CLEANING_CHANNEL_ID).send(discordMessage)

    async def testCron(self):
        await self.client.get_channel(TEST_CHANNEL_ID).send("test cron message")
        return ("discord message","testcron")
    
    # checks
    def checkIsWeekday(self):
        return dt.now().weekday() < 5
    def checkIsWeekend(self):
        return dt.now().weekday() > 4