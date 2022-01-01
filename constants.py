# Will put constants here.

import berserk

# Change this to your own API TOKEN

with open("/Users/ahmedalghafri/Documents/PROJECT_API_TOKENS/lichess_berserk_api_token_api.txt", "r") as f:
    API_TOKEN = f.readline()

SESSION = berserk.TokenSession(API_TOKEN)

CLIENT = berserk.Client(session=SESSION)

