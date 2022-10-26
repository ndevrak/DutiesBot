import json

json_path = "Bot/Duties_func/ids_names.json"
    
def getNames():
    global json_path
    return readJson(json_path)

def readJson(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data
    
def updateJson(filename, newData):
    # Warning : be careful with this updateJson
        # new data is added directly to top level dictionary
    data = readJson(filename)
    for k in newData.keys():
        data[k] = newData[k]
    with open(filename, 'w') as file:
        json.dump(data, file)
    
def updateName(newData):
    global json_path
    # use this most of the time, not updateJson
    # it makes sure that code internal name values match the json
    updateJson(json_path, newData)

def checkID(atAuthor):
    return atAuthor in getNames().keys()

def checkName(name):
    return name in getNames().values()

def getNameFromID(atAuthor):
    if checkID(atAuthor):
        return getNames()[atAuthor]

def getIDFromName(name):
    # might break with multiple people with the same last name, but whatever :)
    data = getNames()
    return list({key for key in data if data[key] == name})[0]