import json

class NameHandler:
    def __init__(self, json_path = "ids_names.json"):
        self.ids_names_path = json_path
        self.ids_names = self.readJson(self.ids_names_path)
    
    def getNames(self):
        return self.ids_names

    def readJson(self,filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    
    def updateJson(self, filename, newData):
        # Warning : be careful with this updateJson
            # new data is added directly to top level dictionary
        data = self.readJson(filename)
        for k in newData.keys():
            data[k] = newData[k]
        with open(filename, 'w') as file:
            json.dump(data, file)
    
    def updateName(self, newData):
        # use this most of the time, not updateJson
        # it makes sure that code internal name values match the json
        self.updateJson(self.ids_names_path, newData)
        self.ids_names = self.readJson(self.ids_names_path)
    
    def checkID(self, atAuthor):
        return atAuthor in self.ids_names.keys()

    def getNameFromID(self, atAuthor):
        if self.checkID(atAuthor):
            return self.ids_names[atAuthor]
        return False

    def getIDFromName(self, name):
        # might break with multiple people with the same last name, but whatever :)
        return list({key for key in self.ids_names if self.ids_names[key] == name})[0]