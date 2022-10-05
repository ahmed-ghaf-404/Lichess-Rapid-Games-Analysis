'''
 * @author Ahmed Alghafri
 * @email alghaf.ahmd@gmail.com
 * @create date 01-01-2022 17:03:09
 * @modify date 01-01-2022 17:03:09
 * @desc This code generates a dataset containing data of chess games played on lichess.org
'''

import pandas as pd

import constants as C
import json
import os
import pickle


def write_usernames_in_txt(games, is_csv=True):
    if is_csv:
        with open(r'Data\Usernames\username.txt', 'w') as f:
            for i in range(len(games)):
                f.write('{0}\n'.format(games['Username'][i]))
    
    else:
        with open(r'Data\Usernames\username.txt', 'w') as f:
            for i in games:
                f.write(str(i))


def generate_username_set(csv_file_path:str):
    '''
    This function takes a CSV file that contain records of chess games from lichess.org and return a Set of all the lichess usernames.

    Args:
        csv_file_path (String): A string path to a CSV file that contains lichess.org usernamedata

    returns: 
        Set<String> containing usernames
    '''
    
    # USES:
    # 
    # The generated set will be used to scrape new games (data)
    #
    df = pd.read_csv(csv_file_path)
    usernames = set()

    # for index, row in df.iterrows():
    #     usernames.add(row['Username'])
    # # Attempts to read a previous username set
    

    
    return usernames


def write_usernames(username_set:set, output_path=r'Data\Usernames'):
    """Saves username_set in a pickle file for future uses

    Args:
        username_set (set): A set of liches.org usernames
    """        
    with open(r"{}\username_set.pkl".format(output_path), "wb") as f:
        pickle.dump(username_set, f)
    
    return

def read_usernames(username_path: str, current_username_set: set = set(), is_txt=False) -> set:
    """reads usernames from a saved pickle. Also adds any locally added usernames if available.
    

    Args:
        username_path (str): path to the pickle file
        current_username_set DEFAULT -> set(): in case there was an exsisting set

    Returns:
        set: a set of lichess.org usernames
    """
    if is_txt:
        username_set = set(line.strip() for line in open(username_path))
        print(username_set)
    else:
        with open(username_path, "rb") as f:
            username_set = pickle.load(f)
        
    for i in current_username_set:
        username_set.add(i)

    return username_set


def generate_final_dataset(games_path:str = "Data/Games") -> pd.DataFrame:
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



