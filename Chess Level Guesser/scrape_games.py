import os
import sys
import time
import constants as C
import random
import json

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

if __name__=='__main__':
    scrape_games(sys.argv[0], sys.argv[1], sys.argv[2])