import psycopg2
import json
import os
import _utility
# Connecting
conn = psycopg2.connect(
            host='localhost',
            database='lichessrapiddb',
            user='ahmedalghafri',
            password='postgres'
)
# cursor
cur = conn.cursor()

############## START DB SET UP ##############
cur.execute("""CREATE TABLE IF NOT EXISTS games(
    gameId text PRIMARY KEY,
    status text,
    whiteID text,
    blackID text,
    eco text,
    moves text,
    winnerIsWhite boolean,
    isDraw boolean);
    """)
cur.execute("""CREATE TABLE IF NOT EXISTS gameStats(
    gameId text PRIMARY KEY,
    status text,
    whiteID text,
    whiteRating int,
    whiteInaccuracy int,
    whiteMistake int,
    whiteBlunder int,
    whiteACPL int,
    blackID text,
    blackRating int,
    blackInaccuracy int,
    blackMistake int,
    blackBlunder int,
    blackACPL int,
    openingName text,
    eco text,
    ply int,
    moves text[],
    eval int[]
    );
    """)
############## END DB SET UP ##############

############## START POPULATING DB ##############
scraped_games_path = "./Data/Scraped_Files"
def addGameEntry(path):
    with open(path, 'r') as f:
        '''
        gameId text PRIMARY KEY,
        status text,
        whiteID text,
        blackID text,
        eco text,
        moves text[],
        winnerIsWhite boolean);
        '''
        game = json.load(f)
        gameID = game['id']
        status = game['status']
        whiteID = game['players']['white']['user']['id']
        blackID = game['players']['black']['user']['id']
        eco = game['opening']['eco']
        moves = game['moves']
        if 'winner' in game:
            winnerIsWhite = game['winner'] == 'white'
            isDraw = False
        else:
            winnerIsWhite = False
            isDraw = True


        cur.execute("INSERT INTO games VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (gameID, status, whiteID, blackID, eco, moves, winnerIsWhite, isDraw))
    return 
def populateGamesTable(path):
    for subdir, dirs, files in os.walk(path):
        for filename in files:
        # loop through all of this player's games
        # for filename in os.listdir(path):
            f = os.path.join(subdir, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # try: 
                if _utility.validateGame(f):
                    addGameEntry(f)
                # except Exception as e:
                    # _utility.deleteGame(f)
    return
populateGamesTable(scraped_games_path)

############## END POPULATING DB ##############

############## START COMANDS ##############
############## START TESTING CONNECTION ##############
cur.execute("""SELECT * FROM games;""")
result = cur.fetchall()
print(result)
############## END TESTING CONNECTION ##############


############## END COMANDS ##############

# closing cursor and connection safely
cur.close()
conn.close()
print('terminating....')