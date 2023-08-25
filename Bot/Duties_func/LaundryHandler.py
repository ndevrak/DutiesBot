import yaml
from datetime import datetime as dt
from constants import *

wash_time_def = 29
dry_time_def = 45

laundry_yaml_path = "Bot/yamls/laundry.yaml"
laundry_log_path = "Bot/yamls/laundry_log.csv"

def readLaundryYAML():
    global laundry_yaml_path
    with open(laundry_yaml_path,'r') as file:
        data = yaml.safe_load(file)
    return data

def updateLaundryYAML(newData):
    global laundry_yaml_path
    data = readLaundryYAML()
    for k in newData.keys():
        data[k].update(newData[k])
    with open(laundry_yaml_path, 'w') as file:
        yaml.safe_dump(data, file)

def getMachines():
    return readLaundryYAML()

def getMachine(machine):
    return getMachines()[machine]

def setMachine(machine, atAuth, runTime):
    #data = getMachine(machine)
    newData = {machine : {"lastRan":dt.now().strftime(TIME_FMT),
                          "whoRan" : atAuth, 
                          "runTime" : int(runTime), 
                          "notified" : 0}}
    updateLaundryYAML(newData)

def minTillDone(machine):
    data = getMachine(machine)
    now = dt.now()
    machineStart = dt.strptime(data["lastRan"], TIME_FMT)
    minutes = int(data["runTime"] - (now-machineStart).total_seconds()/60)
    return minutes

def updateNotified(machine, noti = 1):
    updateLaundryYAML({machine:{"notified" : noti}})

def laundrylog(ctx):
    data = {}
    data["time"] = dt.now().strftime(TIME_FMT)
    data["command"] = ctx.command.name
    data["run_by_ID"] = ctx.author.mention