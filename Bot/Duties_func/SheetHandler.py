import gspread
from oauth2client.service_account import ServiceAccountCredentials

from constants import *

# Get Sheet and Duties info -------------------------
def getSheetInfo(sheet):
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'Bot/yamls/sheets_api.json', scope)
    client = gspread.authorize(creds)
    # Open Duties Spreadsheet
    ss = client.open_by_key(SHEET_KEY)
    # return requested sheet
    return ss.worksheet(sheet)

def getDutyInfo(name, data = None):
    # allows a fixed set of data to be used to reduce sheets api calls
    if data == None:
        data = getSheetInfo('[Duties]').get_all_values()
    # empty dictionary for duties info
    outDict = {"duties" : [], "rooms" : [], "floors" :[], "done" : [], "coords" : []}
    # go through rows of data
    for i,e in enumerate(data):
        try:
            nameCol = -1
            while True:
                #name row is just i
                nameRow = i
                #try to find name in the row
                nameCol = e.index(name, nameCol+1)
                #add duty name to outdict
                outDict["duties"].append(data[nameRow][nameCol-2])
                #search vertically for the room name
                roomRow = nameRow
                while not (data[roomRow][nameCol-2] == ""):
                    roomRow -= 1

                #add rooms floors and duty coords to the output
                outDict["rooms"].append(data[roomRow + 1][nameCol-2])
                outDict["floors"].append(data[0][nameCol-2])
                outDict["coords"].append([nameRow+1, nameCol+2])
                #check if duty is done
                if data[nameRow][nameCol+1] == "TRUE":
                    outDict["done"].append(1)
                else:
                    outDict["done"].append(0)
        except ValueError:
            pass
    return outDict
    
def checkOffDuty(coord):
    sheet = getSheetInfo('[Duties]')
    # coord can be gotten from getDutyInfo(name)
    sheet.update_cell(coord[0], coord[1], True)
    #cell = sheet.cell(coord[0], coord[1])
    #cell.value = True
    #sheet.update_cells([cell], value_input_option='USER_ENTERED')