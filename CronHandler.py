from datetime import datetime as dt
import random

from sympy import false

from constants import *
from SheetHandler import *

class CronHandler:
    def __init__(self, client, nameHandler):
        self.actions = {
                        self.tableCron : {"times" : TABLES_TIMES , "run" : RUN_TABLES, "checks" : [self.tableCronCheck]},
                        self.testCron : {"times" : ["1"], "run" : False, "checks" : []}
                        }
        self.client = client
        self.nh = nameHandler
    
    async def cron(self):
        hour = dt.now().strftime(CRON_TIME_FMT)
        day = dt.now().strftime(CRON_DATE_FMT)
        # iterate through actions
        for key in self.actions.keys():
            # if action is set to run
            if self.actions[key]["run"]:
                # if passes all checks
                if self.checkChecks(key):
                    # do the action
                    await key()

    def checkChecks(self, key):
        for check in self.actions[key]["checks"]:
            if not check():
                return False
        return True

    def tableCronCheck(self):
        hour = dt.now().strftime(CRON_TIME_FMT)
        day = dt.now().strftime(CRON_DATE_FMT)
        # if its a weekend
        if dt.now().weekday() > 4:
            return False
        # if its the standard tables times
        if hour in TABLES_TIMES:
            return True
        # if its between standard times and tables have not run yet
        if int(hour) > int(TABLES_TIMES[0]) and int(hour) < int(TABLES_TIMES[1]):
            if getTableInfo()["date"] == day:
                return False
            return True
        # don't run
        return False

    async def tableCron(self):
        # if everyone has cleaned, reset the table
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
        if not person in self.nh.getNames().values():
            discordMessage += "It is " + person + "'s turn to wipe tables today, but their name is not saved.\nTell them to save their name using '.savename LASTNAME'."
        else:
            discordMessage += self.nh.getIDFromName(person) + " it's your turn to wipe tables today."
        await self.client.get_channel(CLEANING_CHANNEL_ID).send(discordMessage)

    async def testCron(self):
        await self.client.get_channel(TEST_CHANNEL_ID).send("test cron message")
        return ("discord message","testcron")