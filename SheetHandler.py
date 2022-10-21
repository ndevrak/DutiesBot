import gspread
from oauth2client.service_account import ServiceAccountCredentials

from constants import *

# Get Sheet and Duties info -------------------------
def getSheetInfo(sheet):
    # WARNING: this method handles duties sheet differently than other sheets
        # for other sheets it just returns the sheet object
        # for duties sheet it returns the values in [0] and the sheet in [1]
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'sheets_api.json', scope)
    client = gspread.authorize(creds)
    # Open Duties Spreadsheet and open current week's sheet
    # ss = client.open('Duties - Fall 2022')
    ss = client.open_by_key(SHEET_KEY)
    if (sheet == 'Duties'):
        dutiesSheet = ss.sheet1
        return [dutiesSheet.get_all_values(), dutiesSheet]
    elif (sheet == 'Lodgers'):
        lodgersSheet = ss.worksheet('Lodgers')
        return lodgersSheet
    elif (sheet == 'Codes'):
        codeSheet = ss.worksheet('Codes')
        return codeSheet
    return

def getDutyInfo(name, data = None):
    # allows a fixed set of data to be used to reduce sheets api calls
    if data == None:
        data = getSheetInfo("Duties")[0]
    # empty dictionary for duties info
    outDict = {"duties" : [], "rooms" : [], "floors" :[], "done" : [], "coords" : []}

    # go through rows of data
    for i,e in enumerate(data):
        try:
            #name row is just i
            nameRow = i
            #try to find name in the row
            nameCol = e.index(name)
            #add duty name to outdict
            outDict["duties"].append(data[nameRow][nameCol-1])
            #search vertically for the room name
            roomRow = nameRow
            while not (data[roomRow][nameCol-1] == ""):
                roomRow -= 1

            #add rooms floors and duty coords to the output
            outDict["rooms"].append(data[roomRow + 1][nameCol-1])
            outDict["floors"].append(data[0][nameCol-1])
            outDict["coords"].append([nameRow+1,nameCol+2])
            #check if duty is done
            if data[nameRow][nameCol+1] == "TRUE":
                outDict["done"].append(1)
            else:
                outDict["done"].append(0)
        except ValueError:
            pass
    return outDict
    
def checkOffDuty(coord):
    sheet = getSheetInfo('Duties')[1]
    # coord can be gotten from getDutyInfo(name)
    sheet.update_cell(coord[0], coord[1], True)
    return

def loadTablesLodgers():
    # fetch sheet data
    data = getSheetInfo("Lodgers").get_all_values()
    # dictionary where key is name and value is if they have cleaned
    outDict = {}
    # enumerate through rows of data
    for i, row in enumerate(data):
        # value in cleaned column and name column
        cleaned = row[LODGER_TABLE_COLUMN]
        name = row[LODGER_COLUMN]
        if (cleaned == "TRUE" or cleaned == "FALSE"):
            outDict[name] = True if cleaned == "TRUE" else False
    return outDict

def notCleanedLodgers():
    # TODO maybe add row index for each name
        # speeds up checking off stuff as well as filling/clearing
    lodgerDict = loadTablesLodgers()
    outlst = []
    for name in lodgerDict.keys():
        if not lodgerDict[name]:
            outlst.append(name)
    return outlst

def checkOffTable(name):
    sheet = getSheetInfo("Lodgers")
    data = sheet.get_all_values()
    for i,row in enumerate(data):
        if row[LODGER_COLUMN] == name:
            sheet.update_cell(i+1, LODGER_TABLE_COLUMN+1, True)

def resetTablesCol(key = "TRUE", value = "FALSE"):
    # TODO optimize with .batch_update or something of the sort
        # currently uses a bunch of api calls
    sheet = getSheetInfo("Lodgers")
    data = sheet.get_all_values()
    for i,row in enumerate(data):  
        if row[LODGER_TABLE_COLUMN] == key:
            sheet.update_cell(i+1, LODGER_TABLE_COLUMN+1, value)

def updateTableCleaner(name, date = None):
    sheet = getSheetInfo("Lodgers")
    sheet.update_acell("F1", name)
    if not date == None:
        sheet.update_acell("E3", date)

def getTableInfo():
    sheet = getSheetInfo("Lodgers")
    data = sheet.get_all_values()
    return {"date":data[2][4], "cleaner":data[0][5]}