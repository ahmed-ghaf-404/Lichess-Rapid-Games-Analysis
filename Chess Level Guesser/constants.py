# Will put constants here.
import berserk
import os

# Change this to your own API TOKEN
API_TOKEN = 'lip_TOowT3Vwf73LPJxNVOUK'
# API_TOKEN = os.environ.get("Lichess-API-Token")

SESSION = berserk.TokenSession(API_TOKEN)

CLIENT = berserk.Client(session=SESSION)

def getScrapedUsernames(path):
    scraped_usernames = set()
    for folder in os.walk(path):
        if path in folder[0]:
            username = folder[0].replace(path,'')[1:]
        scraped_usernames.add(username)
    return scraped_usernames

SCRAPED_USERNAMES = getScrapedUsernames('Data/Scraped_Files')