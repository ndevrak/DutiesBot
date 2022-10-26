import json
from datetime import datetime as dt

wash_time_def = 29
dry_time_def = 45

laundry_json_path = "Bot/Laundry_func/laundry.json"

TIME_FMT = "%y-%m-%d %H:%M"

def readLaundryJson():
    global laundry_json_path
    with open(laundry_json_path,'r') as file:
        data = json.load(file)
    return data

def updateLaundryJson(newData):
    global laundry_json_path
    data = readLaundryJson()
    for k in newData.keys():
        data[k] = newData[k]
    with open(laundry_json_path, 'w') as file:
        json.dump(data, file)

def readMachine(machine):
    data = readLaundryJson()
    return data[machine]

def machineStatus(machine):
    data = readMachine(machine)
    now = dt.now()
    machineStart = dt.strptime(data["lastRan"], TIME_FMT)
    minutes = int(data["runTime"] - (now-machineStart).total_seconds()/60)
    return minutes

def setMachine(machine, atAuth, runTime):
    newData = {machine : {"lastRan":dt.now().strftime(TIME_FMT),"whoRan" : atAuth, "runTime" : int(runTime)  }}
    updateLaundryJson(newData)