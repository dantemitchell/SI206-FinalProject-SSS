import re
import statsapi
import requests
import _sqlite3
import matplotlib as plt
import seaborn as sb
import json

def buildTeamList():
    teamjson = statsapi.get('teams', {'season':'2023'})['teams'] #{'leagueIds':'Major League Baseball'}
    teamLst = []
    for team in teamjson:
        if team['sport']['name'] == "Major League Baseball":

            teamLst.append((team['name'], team['id']))
    return teamLst

def buildStatList(home = True):
    #boxCat = list(statsapi.boxscore_data(statsapi.last_game(140))['homeBatters'][0].values())
    locStr = ""
    if home:
        locStr = "HOME"
    else:
        locStr = "AWAY"
    newBoxCat = [("TeamName", "TEXT"), ("TeamID", "INTEGER"), (f"{locStr}Wins", "INTEGER"), (f"{locStr}Losses", "INTEGER"), (f"{locStr}RScored", "INTEGER"), (f"{locStr}RAllowed", "INTEGER")]
    return newBoxCat
    """for item in boxCat:
        if type(item) == str:
            if item.isupper():
                newStr = f'h{item}'
                newBoxCat.append(newStr)
    pitchCat = list(statsapi.boxscore_data(statsapi.last_game(140))['homePitchers'][0].values())
    newPitchCat = []
    for item in pitchCat:
        if type(item) == str:
            if item.isupper():
                newStr = f'p{item}'
                newPitchCat.append(newStr)
    for i in newPitchCat:
        newBoxCat.append(i)
    return newBoxCat"""

def createDatabase(statList, dbName, tableName):
    conn = _sqlite3.connect(dbName)
    cursor = conn.cursor()
    # Check if the table already exists
    existing_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}';"
    cursor.execute(existing_table_query)
    existing_table = cursor.fetchone()

    # If the table exists, drop it
    if existing_table:
        drop_table_query = f"DROP TABLE {tableName};"
        cursor.execute(drop_table_query)
    
    columns_definition = ', '.join(f'{column} {datatype}' for column, datatype in statList)
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {tableName} (
        {columns_definition}
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def processBoxScore(gamePk):
    game = statsapi.game_scoring_play_data(gamePk)
    homeTeam = game['home']['name']
    homeId = game['home']['team_id']
    awayTeam = game['away']['name']
    awayId = game['away']['team_id']
    homeScore = game['plays'][-1]['result']['homeScore']
    awayScore = game['plays'][-1]['result']['awayScore']
    homeTeamWin = homeScore > awayScore
    awayTeamWin = awayScore > homeScore
    return (homeTeam, homeId, homeTeamWin, homeScore, awayScore), (awayTeam, awayId, awayTeamWin, awayScore, homeScore)

def createDataDict(season):
    resultsDict = {}
    season_startdate, season_enddate = statsapi.get('season', {'seasonId': season, 'sportId': 1})['seasons'][0]['regularSeasonStartDate'], statsapi.get('season', {'seasonId': season, 'sportId': 1})['seasons'][0]['regularSeasonEndDate'], 
    firstgamepk = statsapi.get('schedule', {'sportId': 1, 'date': season_startdate})['dates'][0]['games'][0]['gamePk']
    lastgamepk = statsapi.get('schedule', {'sportId': 1, 'date': season_enddate})['dates'][0]['games'][-1]['gamePk']
    for gamepk in range(firstgamepk, lastgamepk + 1): 
        homeData, awayData = processBoxScore(gamepk)
        if homeData[0] not in resultsDict:
            homeWin = 0
            homeLoss = 0
            if homeData[2] == True:
                homeWin = 1
            else:
                homeLoss = 1
            innerDict = {'TeamID': homeData[1], 'HOMEWins' : homeWin, 'HOMELosses': homeLoss, "HOMERScored": homeData[3], 'HOMERAllowed': homeData[4]}
            resultsDict[homeData[0]] = innerDict
            


def populateTable():
    divisionLst = [200,201,202,203,204,205]
    print(statsapi.standings_data(leagueId="103,104", division="all", include_wildcard=False, season=2022, standingsTypes=None, date=None)[200]['teams'][0].keys())
    for division in divisionLst:
        for i in range(0,5):
            teamDict = statsapi.standings_data(leagueId="103,104", division="all", include_wildcard=False, season=2022)[division]['teams'][i]
            teamName = teamDict['name']
            teamId = teamDict['team_id']
            seasonWins = teamDict



def main():
    teamLst = buildTeamList()
    statLst = buildStatList(True)
    #createDatabase(statLst, "Baseball Data.db", "HomeData")
    #createDatabase(statLst, "Baseball Data.db", "AwayData")
    #populateTable()
    #processBoxScore(gamePk)
    createDataDict('2023')



main()