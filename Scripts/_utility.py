import pandas as pd
import datetime
import constants as C
import json
import os
from DatabaseManager import DatabaseManager

class Utility:
    def __int__(self, databaseManager:DatabaseManager):
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

        # print('scraping {} game(s) the username: {}'.format(num_of_games, username))
        new_username_set = set()
        try:
            gameLists = C.CLIENT.games.export_by_player(username=username, as_pgn=False, max=num_of_games,rated=True,perf_type="rapid", analysed=True, moves=True, evals=True,opening=True)
            for game in gameLists:
                if not os.path.isdir("{}/{}".format(path,username)):
                    os.mkdir("{}/{}".format(path,username))
                if os.path.isfile(f"{path}{username}/{game['id']}.json"):
                    continue
                if is_need_more_players:
                    new_username_set.add(game["players"]["white"]["user"]["name"])
                    new_username_set.add(game["players"]["black"]["user"]["name"])
                with open(f"{path}{username}/{game['id']}.json", 'w') as f:
                    if self.validateGame(f"{path}{username}/{game['id']}.json"):
                        json.dump(game, f, indent=4, sort_keys=False, default=str)
        except Exception as e:
            print(e)
        
        return new_username_set

    def validateGame(self, path:str):
        with open(path, 'r') as f:
            game = json.load(f)
            if game['variant']!='standard':
                # sus game
                filename = path.split('/')[-1]
                # ! DANGEROUS
                os.rename(path, f'./Data/SusGames/{filename}')
                print(game['variant'])
                return False
        
        return True

if __name__ == '__main__':
    util = Utility(DatabaseManager())
    util.validateGame("Data/Scraped_Files/RatchetLodross/fOBrhnyQ.json")
        