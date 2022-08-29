import time
import pandas as pd
import datetime
import constants as C
import json
import os

def getUsernameSet(csv_path: str):
    '''
    PARAM: 
        csv_path String: path to the CSV file containing usernames
    
    RETURN:
        username_set Set: contains all usernames we know
    '''
    csv = pd.read_csv(csv_path)
    username_set = set()
    for index, row in csv.iterrows():
        username_set.add(row['Username'])    
    return username_set

def createUsernameCSV(username_set: set):
    '''
    PARAM:
    username_set Set: set containing all usernames we have so far. 
    
    Creates a new CSV file

    RETURN:
    None
    '''
    df = pd.DataFrame()
    df['Username'] = list(username_set)
    df.to_csv('Data/Prepared_Data/Usernames-{}.csv'.format(datetime.datetime.now()))
    return 

def scrape_n_rapid_games(username:str, num_of_games:int=1):
    '''
    PARAM:
        username String: a lichess username
    Creates a JSON file containing the game review data
    '''
    print('scraping {} game(s) the username: {}'.format(num_of_games, username))
    new_username_set = set()
    try:
        for game in C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=num_of_games,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True):
            if not os.path.isdir("Data/Scraped_Files/{}".format(username)):
                os.mkdir("Data/Scraped_Files/{}".format(username))
            with open("Data/Scraped_Files/{}/{}.json".format(username, game['id']), 'w') as f:
                json.dump(game, f, indent=4, sort_keys=False, default=str)
            new_username_set.add(game["players"]["white"]["user"]["name"])
            new_username_set.add(game["players"]["black"]["user"]["name"])
            time.sleep(0.1)
    except Exception as e:
        raise e
    
    return new_username_set


def buildDataset(path="Data/Scraped_Files"):
    # path here is the path to the data folder
    # It's currently at Data/Scraped_Files
    def buildRow(path):
        # path here is the path to the players folder
        # It's currently at Data/Scraped_Files/username
        return
    
    for username in os.walk(path):
        print(username)
        
    return
