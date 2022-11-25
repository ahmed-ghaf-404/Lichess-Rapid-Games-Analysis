from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import os 
import json

class DatabaseManager:
    def __init__(self, host='localhost', database='lichessrapiddb', user='ahmedalghafri', password='postgres', port=5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        
        # connect to DB
        self.connectDB()
        
        self.alchemyEngine = create_engine(url="postgresql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database))
        # setup the database
        # create tables
        self.setupDB()

        try:
            self.userIds = {i[0] for i in self.runCommand("SELECT userId from users;")}
            self.connectDB()
        except Exception as _:
            self.userIds = set()
        try:
            self.gameIds = {i[0] for i in self.runCommand("SELECT gameId from games;")}
            self.connectDB()
        except Exception as _:
            self.gameIds = set()
        
        try:
            self.gameStatsIds = {i[0] for i in self.runCommand("SELECT gameId from gameStats;")}
            self.connectDB()
        except Exception as _:
            self.gameStatsIds = set()

        # print(self.gameIds)
        self.conn.commit()
        self.closeDatabase()


    def connectDB(self):
        # Connecting
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
        )
        # cursor
        self.cur = self.conn.cursor()
    def setupDB(self):
        ############## START DB SET UP ##############
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
            userId VARCHAR(20),
            title char(3),
            rating int,
            PRIMARY KEY(userId)
        );
        """)
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS games(
            gameId VARCHAR(10) PRIMARY KEY,
            status text,
            whiteID VARCHAR(20) references users(userId),
            blackID VARCHAR(20) references users(userId),
            eco text,
            moves text[],
            winner int);""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS gameStats(
            gameId VARCHAR(10) PRIMARY KEY,
            status text,
            whiteID VARCHAR(20) references users(userID),
            whiteRating int,
            whiteInaccuracy int,
            whiteMistake int,
            whiteBlunder int,
            whiteACPL int,
            blackID VARCHAR(20) references users(userID),
            blackRating int,
            blackInaccuracy int,
            blackMistake int,
            blackBlunder int,
            blackACPL int,
            openingName text,
            eco text,
            ply int,
            moves text[],
            eval int[],
            winner int
            );
            """)
        self.conn.commit()
        return 
    def closeDatabase(self):
        '''closing cursor and connection safely'''
        self.cur.close()
        self.conn.close()
        print('terminating database....')
############## END DB SET UP ##############
# 
############## START POPULATING DB ##############
    def populateUsersTable(self,path="./Data/Scraped_Files/"):
        '''
        userId text,
        title char(3),
        rating int,
        PRIMARY KEY(userId)
        '''
        def GetUsersEntry() -> set: 
            print("Creating creating values to add to users table")
            users_table_set = set()
            # Add a new user to user table
            for user in os.listdir(path):
                # we're in the users folder
                # we have access to indivisual users
                if not os.path.isdir(path+user):
                    print(f'{path+user} was skipped')
                    continue
                
                for game in os.listdir(f"{path}/{user}"):
                    # we're in the user folder
                    # we have access to indivisual games
                    with open(path+user+'/'+game) as f:
                        game = json.load(f)['players']
                        
                        userId = game['white']['user']['id']

                        try:
                            title = game['white']['user']['title']
                        except Exception as e:
                            title = None
                        rating = game['white']['rating']
                        users_table_set.add((userId,title,rating))
                        
                        userId = game['black']['user']['id']

                        try:
                            title = game['black']['user']['title']
                        except Exception as e:
                            title = None
                        rating = game['black']['rating']
                        users_table_set.add((userId,title,rating))
            print(f"Done creating values to add to users table: {len(users_table_set)} element")
            return users_table_set
        s = GetUsersEntry()
        cmd = "INSERT INTO users (userId, title, rating) VALUES "
        for entry in s:
            userId, title, rating = entry
            if userId not in self.userIds:
                self.userIds.add(userId)
                title = f"'{title}'" if title is not None else 'NULL'
                cmd += f"('{userId}', {title}, {rating}),"
            else:
                print(entry)
        cmd = cmd[:-1]
        if cmd[-1] != ')':
            return
        cmd += ';'

        try:
            with open('Data/Commands/insert_users.txt', 'w+') as f:
                f.write(cmd)
        except Exception as _:
            with open('../insert_users.txt', 'w+') as f:
                f.write(cmd)
        
        try:
            self.connectDB()
            self.cur.execute(cmd)
            print("Command has been executed")
            self.conn.commit()
            self.closeDatabase()
        except Exception as e:
            print(e)

        return
    def populateGamesTable(self,path="./Data/Scraped_Files/"):
        def GetGamesEntry() -> set: 
            '''
            gameId VARCHAR(10) PRIMARY KEY,
            status VARCHAR(3),
            whiteID VARCHAR(20) references users(userId),
            blackID VARCHAR(20) references users(userId),
            eco text,
            moves text,
            winner int
            '''
            print("Creating creating values to add to games table")
            games_table_set = set()
            # Add a new user to user table
            for user in os.listdir(path):
                # we're in the users folder
                # we have access to indivisual users
                if not os.path.isdir(path+user):
                    continue
                if os.path.getsize(path+user)==0:
                    print(path+user)
                for g in os.listdir(path+user):
                    # we're in the user folder
                    # we have access to indivisual games
                    with open(path+user+'/'+g) as f:
                        game = json.load(f)
                        gameId = game['id']
                        if gameId is not None and gameId not in self.gameIds:
                            self.gameIds.add(gameId)
                        status = game['status']

                        whiteId = game['players']['white']['user']['id']
                        blackId = game['players']['black']['user']['id']
                        eco = game['opening']['eco']
                        moves = game['moves'].replace(' ', "','")
                        moves = "['" + moves + "']"

                        if 'winner' not in game:
                            winner = -1
                        else:
                            winner = 0 if game['winner']=='white' else 1
                        
                        games_table_set.add((gameId,status,whiteId,blackId,eco,moves,winner))
            print(f"Done creating values to add to games table: {len(games_table_set)} element")
            return games_table_set
        s = GetGamesEntry()
        cmd = "INSERT INTO games (gameId,status,whiteId, blackId,eco,moves,winner) VALUES "
        for entry in s:
            gameId,status,whiteId, blackId,eco,moves,winner = entry
            cmd += f"('{gameId}','{status}','{whiteId}','{blackId}','{eco}',ARRAY{moves},{winner}),"
        cmd = cmd[:-1]
        cmd += ';'
        try:
            with open('Data/Commands/insert_games.txt', 'w+') as f:
                f.write(cmd)
        except Exception as e:
            with open("../insert_games.txt", 'w+') as f:
                f.write(cmd)
        try:
            self.connectDB()
            self.cur.execute(cmd)
            print("Command has been executed")
            self.conn.commit()
            self.closeDatabase()
        except Exception as e:
            print(e)
        
        return
    def populateGameStatsTable(self,path="./Data/Scraped_Files/"):
        def GetGameStatsEntry() -> list: 
            '''
            gameId VARCHAR(10) PRIMARY KEY,
            status VARCHAR(3),
            whiteID VARCHAR(20) references users(userId),
            blackID VARCHAR(20) references users(userId),
            eco text,
            moves text,
            winner int
            '''
            print("Creating creating values to add to gameStats table")
            games_table_list = []
            # Add a new user to user table

            for user in os.listdir(path):
                # we're in the users folder
                # we have access to indivisual users
                if not os.path.isdir(path+user):
                    continue
                for g in os.listdir(path+user):
                    # we're in the user folder
                    # we have access to indivisual games
                    with open(path+user+'/'+g) as f:
                        game = json.load(f)

                        gameId = game['id']
                        if gameId not in self.gameStatsIds:
                            self.gameStatsIds.add(gameId)
                        else:
                            continue
                        status = game['status']

                        whiteId = game['players']['white']['user']['id']
                        whiteRating = game['players']['white']['rating']
                        whiteInaccuracy = game['players']['white']['analysis']['inaccuracy']
                        whiteMistakes = game['players']['white']['analysis']['mistake']
                        whiteBlunder = game['players']['white']['analysis']['blunder']
                        whiteACPL = game['players']['white']['analysis']['acpl']
                        
                        blackId = game['players']['black']['user']['id']
                        blackRating = game['players']['black']['rating']
                        blackInaccuracy = game['players']['black']['analysis']['inaccuracy']
                        blackMistakes = game['players']['black']['analysis']['mistake']
                        blackBlunder = game['players']['black']['analysis']['blunder']
                        blackACPL = game['players']['black']['analysis']['acpl']
                        
                        openingName = game['opening']['name']
                        temp = []
                        for i in range(len(openingName)):
                            if openingName[i] == "'":
                                temp.append("'")
                            temp.append(openingName[i])
                        openingName = ''.join(temp)
                        eco = game['opening']['eco']
                        ply = game['opening']['ply']

                        moves = game['moves'].replace(' ', "', '")
                        
                        
                        moves = "['" + moves + "']"
                        
                        
                        eval = []
                        for i in range(len(game['analysis'])):
                            if 'eval' not in game['analysis'][i]:
                                break
                            eval.append(game['analysis'][i]['eval'])

                        if 'winner' not in game:
                            winner = -1
                        else:
                            winner = 0 if game['winner']=='white' else 1
                        
                        games_table_list.append((gameId,status,whiteId,whiteRating,whiteInaccuracy,whiteMistakes,whiteBlunder,whiteACPL,blackId,blackRating,blackInaccuracy,blackMistakes,blackBlunder,blackACPL,openingName,eco,ply,moves,eval,winner))
            print("Done creating values to add to gameStats table")
            return games_table_list
        s = GetGameStatsEntry()
        cmd = "INSERT INTO gameStats (gameId,status,whiteId,whiteRating,whiteInaccuracy,whiteMistake,whiteBlunder,whiteACPL,blackId,blackRating,blackInaccuracy,blackMistake,blackBlunder,blackACPL,openingName,eco,ply,moves,eval,winner) VALUES "
        for entry in s:
            gameId,status,whiteId,whiteRating,whiteInaccuracy,whiteMistakes,whiteBlunder,whiteACPL,blackId,blackRating,blackInaccuracy,blackMistakes,blackBlunder,blackACPL,openingName,eco,ply,moves,eval,winner = entry
            cmd += f"('{gameId}','{status}','{whiteId}',{whiteRating},{whiteInaccuracy},{whiteMistakes},{whiteBlunder},{whiteACPL},'{blackId}',{blackRating},{blackInaccuracy},{blackMistakes},{blackBlunder},{blackACPL},'{openingName}','{eco}',{ply},ARRAY {moves} ,ARRAY{eval},{winner}),"
        cmd = cmd[:-1]
        cmd += ';'
        try:
            with open('Data/Commands/insert_gamestats.txt', 'w+') as f:
                f.write(cmd)
        except Exception as _:
            with open('../insert_gamestats.txt', 'w+') as f:
                f.write(cmd)

        try:
            self.connectDB()
            self.cur.execute(cmd)
            print("Command has been executed")
            self.conn.commit()
            self.closeDatabase()
        except Exception as e:
            print(e)
        
        return
    
    def runCommand(self, cmd:str):
        result = None
        try:
            self.connectDB()
            self.cur.execute(cmd)
            try:
                result = self.cur.fetchall()
            except Exception as e:
                result = None
            self.conn.commit()
            self.closeDatabase()
        except Exception as e:
            print(e)
        return result

    def getDataFrame(self, cmd: str):
        
        alchemyConn = self.alchemyEngine.connect()
        df = pd.read_sql_query(cmd, con=alchemyConn)
        alchemyConn.close()
        return df
    
if __name__=='__main__':
    db = DatabaseManager()
    ############## START POPULATING DB ##############
    
    # # ? Adding users
    try:
        db.populateUsersTable()
    except Exception as e:
        print(e)
    
    # # ? Adding games
    try:
        db.populateGamesTable()
    except Exception as e:
        print(e)
    

    # # ? Adding game stats
    try:
        db.populateGameStatsTable()
    except Exception as e:
        print(e)
    

    ############## END POPULATING DB ##############

    ############## START COMANDS ##############
    ############## START TESTING CONNECTION ##############
    # db.selectQuery("users")
    ############## END TESTING CONNECTION ##############


    ############## END COMANDS ##############
    
