# MINECRAFT STATISTICS DATA CONVERTER
# EliConstructor 2023
# 
# Stats files from servers should be arranged in a folder in the same directory like so:
#
# dataconverter.py
# data
# |-Server 1
# | |-uuid1.json
# | |-uuid2.json
# | |-uuid3.json
# |-Server 2
# | |-uuid1.json
# | |-uuid2.json
# | |-uuid3.json
#
# Output goes into a folder called "out"

import json
import os
import copy

def getDataFormat(data):
    if 'stats' in data.keys():
        return "new"
    else:
        return "old"

def getCustomStat(data, oldName, newName):
    return getStat(data, oldName, "minecraft:custom", newName)

def getStat(data, oldName, newCategory, newName):
    dataFormat = getDataFormat(data)
    if 'stats' in data.keys():
        dataFormat = "new"
    else:
        dataFormat = "old"

    if dataFormat == "new":
        if newCategory in data["stats"].keys():
            if newName in data["stats"][newCategory].keys():
                return data["stats"][newCategory][newName]
    else:
        if oldName in data.keys():
            return data[oldName]

    return 0

def removeNamespace(string):
    listOfWords = string.split(':', 1)
    if len(listOfWords) > 1: 
        return listOfWords[1]
    return string

def getListStat(data, oldList, newList):
    items = {}
    dataFormat = getDataFormat(data)
    try:
        if dataFormat == "new":
            for item in data["stats"][newList]:
                translatedItem = item
                translatedItem = removeNamespace(translatedItem).lower()
                items[translatedItem] = data["stats"][newList][item]
        else:
            for item in data:
                if item.startswith(oldList):
                    translatedItem = item.replace(oldList, "").replace(".", ":")
                    translatedItem = removeNamespace(translatedItem).lower()
                    items[translatedItem] = data[item]
    except:
        print("An error occurred getting the list stat " + oldList  + "/" + newList + "!")

    return items

    

def getNumericalStatsFromJSON(jsonData):
    stats = {}

    print("Getting singular stats...")
    stats["playtimeHours"] = getCustomStat(jsonData, "stat.playOneMinute", "minecraft:play_time") / 20 / 60 / 60
    stats["metresWalked"] = getCustomStat(jsonData, "stat.walkOneCm", "minecraft:walk_one_cm") / 100
    stats["metresSprinted"] = getCustomStat(jsonData, "stat.sprintOneCm", "minecraft:sprint_one_cm") / 100
    stats["metresCrouched"] = getCustomStat(jsonData, "stat.crouchOneCm", "minecraft:crouch_one_cm") / 100
    stats["metresSwam"] = getCustomStat(jsonData, "stat.swimOneCm", "minecraft:swim_one_cm") / 100
    stats["metresFallen"] = getCustomStat(jsonData, "stat.fallOneCm", "minecraft:fall_one_cm") / 100
    stats["metresByBoat"] = getCustomStat(jsonData, "stat.boatOneCm", "minecraft:boat_one_cm") / 100
    stats["metresByHorse"] = getCustomStat(jsonData, "stat.horseOneCm", "minecraft:horse_one_cm") / 100
    stats["metresByElytra"] = getCustomStat(jsonData, "stat.aviateOneCm", "minecraft:aviate_one_cm") / 100
    stats["metresWalkedUnderwater"] = getCustomStat(jsonData, "stat.diveOneCm", "minecraft:walk_under_water_one_cm") / 100
    stats["metresFlown"] = getCustomStat(jsonData, "stat.flyOneCm", "minecraft:fly_one_cm") / 100
    stats["jumps"] = getCustomStat(jsonData, "stat.jump", "minecraft:jump")
    stats["gamesQuit"] = getCustomStat(jsonData, "stat.leaveGame", "minecraft:leave_game")
    stats["deaths"] = getCustomStat(jsonData, "stat.deaths", "minecraft:deaths")
    stats["mobsKilled"] = getCustomStat(jsonData, "stat.mobKills", "minecraft:mob_kills")
    stats["playersKilled"] = getCustomStat(jsonData, "stat.playerKills", "minecraft:player_kills")
    stats["deathsByPlayer"] = getStat(jsonData, "notinoldformat", "minecraft:killed_by", "minecraft:player")
    stats["sneakTimeHours"] = getCustomStat(jsonData, "stat.sneakTime", "minecraft:sneak_time") / 20 / 60 / 60

    print("Getting list stats...")
    stats["brokenBlocks"] = getListStat(jsonData, "stat.mineBlock.", "minecraft:mined")
    stats["usedItems"] = getListStat(jsonData, "stat.useItem.", "minecraft:used")
    stats["killedBy"] = getListStat(jsonData, "stat.entityKilledBy.", "minecraft:killed_by")
    stats["craftedItems"] = getListStat(jsonData, "stat.craftItem.", "minecraft:crafted")
    stats["pickedUpItems"] = getListStat(jsonData, "stat.pickup.", "minecraft:picked_up")
    stats["killedMobs"] = getListStat(jsonData, "stat.killEntity.", "minecraft:killed")

    return stats


print("Beginning stats extraction...")
statsByUUID = {}

# Get list of directories in data folder
# Directories represent servers
for serverDir in os.listdir("data"):
    print("Extracting stats for server: " + serverDir)
    # For each user on that server
    for userFile in os.listdir("data/" + serverDir):
        print("Extracting stats for user " + userFile + " on server " + serverDir)
        # Get stats from file
        print("Parsing JSON...")
        f = open("data/" + serverDir + "/" + userFile)
        jsonData = json.loads(f.read())
        f.close()

        print("JSON data is in " + getDataFormat(jsonData) + " format.")

        print("Getting numerical stats")
        numStats = getNumericalStatsFromJSON(jsonData)
        print("Done.")

        uuid = userFile.removesuffix(".json")
        # Add user to dict if not already there
        if uuid not in statsByUUID.keys():
            print("User " + uuid + " is new, adding user's dictionary to main dictionary.")
            statsByUUID[uuid] = {}
        # Add stats to dict
        print("Copying user's server stats to main dictionary.")
        statsByUUID[uuid][serverDir] = copy.deepcopy(numStats)

        # Add stats to combined
        print("Beginning stat combination...")
        if "combined" not in statsByUUID[uuid].keys():
            print("Combined dictionary for user " + uuid + " does not exist. Simply copying stats into combined dictionary.")
            statsByUUID[uuid]["combined"] = copy.deepcopy(numStats)
        else:
            print("Combined dictionary exists.")
            for stat in numStats:
                print("Combining stat " + stat)
                if type(numStats[stat]) is dict:
                    print("Stat " + stat + " is a list stat.")
                    for subStat in numStats[stat]:
                        print("Combining substat " + subStat + " of stat " + stat)
                        if subStat in statsByUUID[uuid]["combined"][stat].keys():
                            statsByUUID[uuid]["combined"][stat][subStat] += numStats[stat][subStat]
                        else:
                            statsByUUID[uuid]["combined"][stat][subStat] = numStats[stat][subStat]
                else:
                    if stat in statsByUUID[uuid]["combined"].keys():
                        statsByUUID[uuid]["combined"][stat] += numStats[stat]
                    else:
                        statsByUUID[uuid]["combined"][stat] = copy.deepcopy(numStats[stat])

print("Creating list stat rank lists...")
# Sort list stats
statsCopy = copy.deepcopy(statsByUUID)
for uuid in statsCopy:
    # Numeric stats
    for stat in statsCopy[uuid]["combined"]:        
        if type(statsByUUID[uuid]["combined"][stat]) is not dict:
            sortableDict = {}
            for server in statsCopy[uuid]:
                if server != "combined":
                    sortableDict[server] = statsByUUID[uuid][server][stat]
            statsByUUID[uuid][stat + "Ranked"] = []
            for key, value in sorted(sortableDict.items(), key=lambda item: item[1]):
                statsByUUID[uuid][stat + "Ranked"].insert(0, key)

    # List stats
    for server in statsCopy[uuid]:
        for stat in statsCopy[uuid][server]:
            if type(statsByUUID[uuid][server][stat]) is dict:
                statsByUUID[uuid][server][stat + "Ranked"] = []
                for key, value in sorted(statsByUUID[uuid][server][stat].items(), key=lambda item: item[1]):
                    statsByUUID[uuid][server][stat + "Ranked"].insert(0, key)

print("Creating total list stats...")          
# Total list stats
for uuid in statsCopy:
    for server in statsCopy[uuid]:
        for stat in statsCopy[uuid][server]:
            if type(statsByUUID[uuid][server][stat]) is dict:
                statsByUUID[uuid][server][stat + "Total"] = 0
                for subStat in statsCopy[uuid][server][stat]:
                    statsByUUID[uuid][server][stat + "Total"] += statsCopy[uuid][server][stat][subStat]



print("Saving output...")
if not os.path.exists("out"):
        os.mkdir("out")
for uuid in statsByUUID:
    print("Writing " + uuid + ".json")
    f = open("out/" + uuid + ".json", "w")
    f.write(json.dumps(statsByUUID[uuid]))
    f.close()


#print(statsByUUID["ace947b7-db39-458b-81f3-46495c08501c"]["Europe"]["usedItems"]["minecraft:netherrack"]) # Gets how many times netherrack was place on the Europe server
#print(statsByUUID["ace947b7-db39-458b-81f3-46495c08501c"]["combined"]["brokenBlocks"]["minecraft:wheat"]) # Gets how many times wheat was broken in all servers
#print(statsByUUID["ace947b7-db39-458b-81f3-46495c08501c"]["combined"]["brokenBlocksRanked"][0]) # Gets most broken block in all servers
#print(statsByUUID["ace947b7-db39-458b-81f3-46495c08501c"]["playtimeHoursRanked"][1]) # Gets most broken block in all servers
