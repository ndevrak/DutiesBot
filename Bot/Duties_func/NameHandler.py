import yaml

yaml_path = "Bot/yamls/ids_names.yaml"

def readYAML():
    global yaml_path
    with open(yaml_path,'r') as file:
        data = yaml.safe_load(file)
    return data

def updateYAML(newData):
    global yaml_path
    data = readYAML()
    for k in newData.keys():
        data[k] = newData[k]
    with open(yaml_path, 'w') as file:
        yaml.safe_dump(data, file)

def getNames():
    return readYAML()
    
def updateName(newData):
    global yaml_path
    # use this most of the time, not updateYAML
    # it makes sure that code internal name values match the yaml
    updateYAML(newData)

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