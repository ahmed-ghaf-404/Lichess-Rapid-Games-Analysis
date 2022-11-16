import psycopg2

class DatabaseManager:
    def __init__(self, host='localhost', database='lichessrapiddb', user='ahmedalghafri', password='postgres'):
        # Connecting
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        # cursor
        self.cur = self.conn.cursor()
        
        # setup the database
        # create tables
        self.setupDB()


    def setupDB(self):
        ############## START DB SET UP ##############
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
            userId VARCHAR(20),
            title char(3),
            rating int,
            PRIMARY KEY(userId)
        );
        """)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS games(
            gameId VARCHAR(10) PRIMARY KEY,
            status VARCHAR(3),
            whiteID VARCHAR(20) references users(userId),
            blackID VARCHAR(20) references users(userId),
            eco text,
            moves text,
            winner int
            );
            """)
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
            
        return
############## END DB SET UP ##############
# 
############## START POPULATING DB ##############
    def addUserEntry(self, userId, title, rating):
        '''
        userId text,
        title char(3),
        rating int,
        PRIMARY KEY(userId)
        '''
        try:
            self.cur.execute("INSERT INTO users VALUES (%s, %s, %s)", (userId, title, rating))
        except Exception as e:
            print(e)
        return      

    def addGameStatsEntry(self, gameId,status,whiteId,whiteRating,whiteInaccuracy,whiteMistake,whiteBlunder,whiteACPL,blackId,blackRating,blackInaccuracy,blackMistake,blackBlunder,blackACPL,openingName,eco,ply,moves,eval, winner):
        def addGameEntry():
            try:
                self.cur.execute("INSERT INTO games VALUES (%s, %s, %s, %s, %s, %s, %s)", (gameId, status, whiteId, blackId, eco, moves, winner))
            except Exception as e:
                print(e)
            return
        '''
        self, gameId,status,whiteID,whiteRating,whiteInaccuracy,whiteMistake,whiteBlunder,whiteACPL,blackID,blackRating,blackInaccuracy,blackMistake,blackBlunder,blackACPL,openingName,eco,ply,moves,eval
        '''
        try:
            self.cur.execute("INSERT INTO games VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (gameId,status,whiteId,whiteRating,whiteInaccuracy,whiteMistake,whiteBlunder,whiteACPL,blackId,blackRating,blackInaccuracy,blackMistake,blackBlunder,blackACPL,openingName,eco,ply,moves,eval, winner))
        except Exception as e:
            print(e)
        
        try:
            addGameEntry();
        except Exception as e:
            print("Error in DatabaseManager.addGameEntry():",e)

        return

    def selectQuery(self, table, column='*'):
        """
        DOCUMENTATION:
            prints the results of:
            SELECT {column} FROM {table};
        """
        self.cur.execute("""SELECT {} FROM {};""".format(column, table))
        print(self.cur.fetchall())


    def closeDatabase(self):
        '''closing cursor and connection safely'''
        self.cur.close()
        self.conn.close()
        print('terminating database....')

if __name__=='__main__':
    db = DatabaseManager()
    ############## START POPULATING DB ##############
    db.addUserEntry("EricRosen","IM",2397)
    

    ############## END POPULATING DB ##############

    ############## START COMANDS ##############
    ############## START TESTING CONNECTION ##############
    db.selectQuery("users")
    ############## END TESTING CONNECTION ##############


    ############## END COMANDS ##############

    db.closeDatabase()
    pass
