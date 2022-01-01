'''
 * @author Ahmed Alghafri
 * @email alghaf.ahmd@gmail.com
 * @create date 01-01-2022 17:03:09
 * @modify date 01-01-2022 17:03:09
 * @desc This code generates a dataset containing data of chess games played on lichess.org
'''

import pandas as pd
import time
import constants as C
import json
import random
import os

def generate_username_set(csv_file_path:str) -> tuple:
    """
    This function takes a CSV file that contain records of chess games from lichess.org and return a Set of all the lichess usernames.

    Args:
        csv_file_path (String): A string path to a CSV file that contains lichess.org chess games

    returns: 
        A tuple containing:
            1- usernames (Set): A set that contains all the usernames in the CSV games record (dataset)  
            2- games (DataFrame): A cleaned DataFrame with relevant games only
    """    
    
    # USES:
    # 
    # The generated set will be used to scrape new games (data)
    #


    games = pd.read_csv(csv_file_path)
    
    # username set. Will be returned
    usernames = set()

    for i in range(len(games)):
        # add white player to the set
        usernames.add(games['white_id'][i])

        # add black player to the set
        usernames.add(games['black_id'][i])

        if (games['turns'][i] < 10) or (int(games["increment_code"][i].split('+')[0]) <= 10) or (abs(games['white_rating'][i] - games['black_rating'][i]) > 50) or (games['rated'][i] != True):
            games.drop(i, axis=0, inplace=True)

    return (usernames, games)

def scrape(players_set: set, output_path: str):
    """
    This function takes a set of lichess.org usernames, and scrape their games from lichess.org with Berserk API.

    The function also saves those games in JSON files

    Args:
        players_set (set): A set of lichess.org usernames
        output_path (str): The path of the directory where JSON files are doing to be saved at

    """ 

    for username in players_set:
        try:
            for game in C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=10,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True):
            # for game in C.CLIENT.games.export_by_player(player, max=10, rated=True, perf_type='rapid'):
                if "analysis" in game["players"]["white"].keys():
                    if not os.path.isdir(output_path+"/"+username):
                        os.mkdir(output_path+"/"+username)
                    with open("{}/{}/{}.json".format(output_path, username,random.randint(1,9999999999)), 'w') as f:
                        json.dump(game, f, indent=4, sort_keys=False, default=str)

            time.sleep(0.5)
        except Exception as e:
            print("An error has occurred:")
            print(e)
            time.sleep(1)
    
    return None
