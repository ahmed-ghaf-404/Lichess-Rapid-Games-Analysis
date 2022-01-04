'''
 * @author Ahmed Alghafri
 * @email alghaf.ahmd@gmail.com
 * @create date 01-01-2022 17:03:09
 * @modify date 01-01-2022 17:03:09
 * @desc This code generates a dataset containing data of chess games played on lichess.org
'''

import pandas as pd
import time

from pandas.core.frame import DataFrame
import constants as C
import json
import random
import os
import pickle

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

def scrape_games(players_set: set, output_path: str="Data/Games", game_num:int=3) -> set:
    """
    This function takes a set of lichess.org usernames, and scrape their games from lichess.org with Berserk API.

    The function also saves those games in JSON files

    Args:
        players_set (set): A set of lichess.org usernames
        output_path (str): The path of the directory where JSON files are doing to be saved at
        game_num (int): The maximum number of games scraped from lichess.org

    return:
        new_username_set (set): A new set of lichess usernames for future usages
    """ 
    new_username_set = set()
    for username in players_set:
        if not os.path.isdir(output_path+"/"+username) or len(os.listdir(output_path+"/"+username)) < 40:
            if not os.path.isdir(output_path+"/"+username):
                os.mkdir(output_path+"/"+username)
            try:
                for game in C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=game_num,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True):
                    if "analysis" in game["players"]["white"].keys():
                        with open("{}/{}/{}.json".format(output_path, username,random.randint(1,9999999999)), 'w') as f:
                            json.dump(game, f, indent=4, sort_keys=False, default=str)
                    new_username_set.add(game["players"]["white"]["user"]["name"])
                    new_username_set.add(game["players"]["black"]["user"]["name"])

                time.sleep(0.5)
            except Exception as e:
                print("An error has occurred:")
                print(e)
                time.sleep(1)
    return new_username_set

def write_usernames(username_set:set, output_path):
    """Saves username_set in a pickle file for future uses

    Args:
        username_set (set): A set of liches.org usernames
    """

        
    with open("{}.pkl".format(output_path), "wb") as f:
        pickle.dump(username_set, f)
    return

def read_usernames(username_path: str, current_username_set: set = set()) -> set:
    """reads usernames from a saved pickle. Also adds any locally added usernames if available.
    

    Args:
        username_path (str): path to the pickle file
        current_username_set DEFAULT -> set(): in case there was an exsisting set

    Returns:
        set: a set of lichess.org usernames
    """

    with open(username_path, "rb") as f:
        username_set = pickle.load(f)
    
    for i in current_username_set:
        username_set.add(i)

    return username_set


def generate_final_dataset(games_path:str = "Data/Games") -> DataFrame:
    """Generates a CSV file (dataset) of the games found in the directory games_path

    Args:
        games_path (str, optional): path to the saved chess games. Defaults to "Data/Games".

    Returns:
        DataFrame: A dataset in a .csv file format that include all game data
    """
    df = pd.DataFrame(columns = [
                                "Game ID", 
                                "White Rating", 
                                "Black Rating", 
                                "Average Rating",
                                "Opening ECO", 
                                "# of Opening Ply", 

                                "White avg Centi-pawn Loss", 
                                "White # of Inaccuracies", 
                                "White # of Mistakes", 
                                "White # of Blunders", 

                                "Black avg Centi-pawn Loss", 
                                "Black # of Inaccuracies", 
                                "Black # of Mistakes", 
                                "Black # of Blunders"])

    for dir in os.listdir(games_path):
        print("Now working on username: {}".format(dir))
        try:
            for file in os.listdir(games_path + "/" +dir):
                row_list = []
                try:
                    with open(games_path + "/" +dir+"/"+file) as f:
                        game = json.load(f)
                    
                    if "analysis" in game["players"]["white"].keys() and game["variant"]=="standard" and len(game["moves"].split()) >= 16:
                        # "Game ID", "White Rating", "Black Rating", "Opening ECO", "Opening Ply", "White Centi-pawn Loss", "White's Number of Inaccuracies", "White's Number of Mistakes", "White's Number of Blunders", "Black Centi-pawn Loss", "Black's Number of Inaccuracies", "Black's Number of Mistakes", "Black's Number of Blunders"]
                        
                        # game ID
                        row_list.append(game["id"])
                        # White Rating
                        row_list.append(game["players"]["white"]["rating"])
                        # Black Rating
                        row_list.append(game["players"]["black"]["rating"])
                        # Average Rating
                        row_list.append(int((game["players"]["white"]["rating"] + game["players"]["black"]["rating"])/2))
                        # opening ECO
                        row_list.append(game["opening"]["eco"])
                        # opening ply
                        row_list.append(game["opening"]["ply"])
                        row_list.append(game["players"]["white"]["analysis"]['acpl'])
                        row_list.append(game["players"]["white"]["analysis"]['inaccuracy'])
                        row_list.append(game["players"]["white"]["analysis"]['mistake'])
                        row_list.append(game["players"]["white"]["analysis"]['blunder'])
                        row_list.append(game["players"]["black"]["analysis"]['acpl'])
                        row_list.append(game["players"]["black"]["analysis"]['inaccuracy'])
                        row_list.append(game["players"]["black"]["analysis"]['mistake'])
                        row_list.append(game["players"]["black"]["analysis"]['blunder'])
                        
                        
                        # Add new row
                        df.loc[len(df)] = row_list               
                except json.decoder.JSONDecodeError as d:
                    os.remove(dir+"/"+file)
                    print("empty file has been removed")
                except Exception as e:
                    print(e)
        except NotADirectoryError as E:
            print(dir, E) 


    return df



