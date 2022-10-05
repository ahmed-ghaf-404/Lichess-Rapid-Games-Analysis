import pandas as pd
import datetime
import constants as C
import json
import os
import shutil


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
    df.to_csv('Data/Prepared_Data/Usernames-{}.csv'.format(datetime.datetime.now()), index=False)
    return 

def scrape_n_rapid_games(username:str, num_of_games:int=1, duplicate=False, is_need_more_players=False):
    '''
    PARAM:
        username String: a lichess username
        num_of_games int: number of games to scrape
        no_duplicate bool: whether you want to mine an already existing username.
    Creates a JSON file containing the game review data
    '''
    if not duplicate and username in C.SCRAPED_USERNAMES:
        print("{} has already been mined".format(username))
        s =  set()
        s.add(username)
        return s

    # print('scraping {} game(s) the username: {}'.format(num_of_games, username))
    new_username_set = set()
    try:
        for game in C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=num_of_games,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True):
            if not os.path.isdir("Data/Scraped_Files/{}".format(username)):
                os.mkdir("Data/Scraped_Files/{}".format(username))
            with open("Data/Scraped_Files/{}/{}.json".format(username, game['id']), 'w') as f:
                json.dump(game, f, indent=4, sort_keys=False, default=str)
            if is_need_more_players:
                new_username_set.add(game["players"]["white"]["user"]["name"])
                new_username_set.add(game["players"]["black"]["user"]["name"])
    except Exception as e:
        raise e
    
    return new_username_set


def buildDataset(path="Data/Scraped_Files"):
    # path here is the path to the data folder
    # It's currently at Data/Scraped_Files
    def buildRow(path):
        # path here is the path to the players folder
        # It's currently at Data/Scraped_Files/username

        # [id, white, white rating, white average pawn loss, black, black rating, black acpl, time_control, rating_diff, provisional?]


        #! IDEA: (a inaccuracy + b mistake + c blunder + d) / num_moves= acpl
        #! vector-like?

        return
    
    df = pd.DataFrame()
    for username in os.walk(path):
        row = buildRow(username[0])
        df = df.append(row, True)


    return

def deleteGame(path):
    if os.path.isfile(path):
        print('delete' + path)

def validateGame(path):
    with open(path, 'r') as f:
        game = json.load(f)
        if game['variant']!='rapid':
            # sus game
            filename = path.split('/')[-1]
            os.rename(path, f'./Data/SusGames/{filename}')
            return False
    
    return True

if __name__ == '__main__':
    validateGame("./Data/Scraped_Files/RatchetLodross/fOBrhnyQ.json")