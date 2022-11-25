import pandas as pd
import datetime
import constants as C
import json
import os
from DatabaseManager import DatabaseManager

class Helper:
    def __init__(self, databaseManager):
        self.dbManager = databaseManager

    def getUsernameSet(self,csv_path: str):
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

    def createUsernameCSV(self,username_set: set):
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

    def scrape_n_rapid_games(   self, 
                                path:str, 
                                username:str, 
                                num_of_games:int=1, 
                                allow_duplicate=False, 
                                is_need_more_players=False):
        '''
        PARAM:
            username String: a lichess username
            num_of_games int: number of games to scrape
            no_duplicate bool: whether you want to mine an already existing username.
            Creates a JSON file containing the game review data
        '''
        if not allow_duplicate and username in C.SCRAPED_USERNAMES:
            print("{} has already been mined".format(username))
            return 
        game_added_counter = 0
        new_username = None
        # print('scraping {} game(s) the username: {}'.format(num_of_games, username))
        try:
            gameLists = C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=num_of_games,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True)
            for game in gameLists:
                if not os.path.isdir("{}/{}".format(path,username)):
                    os.mkdir("{}/{}".format(path,username))
                if os.path.isfile(f"{path}/{username}/{game['id']}.json"):
                    if os.path.getsize(f"{path}/{username}/{game['id']}.json") == 0:
                        os.remove(f"{path}/{username}/{game['id']}.json")
                        continue
                if is_need_more_players:
                    if username.lower() == game["players"]["white"]["user"]["name"].lower():
                        new_username = game["players"]["black"]["user"]["name"]
                    else:
                        new_username = game["players"]["white"]["user"]["name"]
                with open(f"{path}/{username}/{game['id']}.json", 'w+') as f:
                    json.dump(game, f, indent=4, sort_keys=False, default=str)
                if self.validateGame(f"{path}/{username}/{game['id']}.json"):
                    game_added_counter += 1
                    print(f"{path}/{username}/{game['id']}.json")
                    
        except Exception as e:
            print(e)
        print(f"Added {game_added_counter}/{num_of_games} to {username}")
        return new_username

    def validateGame(self, path:str):
        if os.path.getsize(path) == 0:
            os.remove(path)
            print("empty file removed")
            return False
        with open(path, 'r') as f:
            game = json.load(f)
            if (game['variant']!='standard' or
                'opening' not in game or 
                'provisional' in game['players']['white'] or
                'provisional' in game['players']['black'] or
                abs(game['players']['white']['rating'] - game['players']['black']['rating']) > 100 or 
                len(game['moves'].split(' ')) < 40):    
                return False
            if 'ratingDiff' in game['players']['white']:
                if game['players']['white']['ratingDiff'] + game['players']['black']['ratingDiff'] > 2:
                    return False
                    
        return True

if __name__ == '__main__':
    helper = Helper(DatabaseManager())
    print(helper.scrape_n_rapid_games("Data/Scraped_Files", "ericrosen",50,True,True))
    
        