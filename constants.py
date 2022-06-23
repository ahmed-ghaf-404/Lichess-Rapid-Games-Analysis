# Will put constants here.

import berserk
import os

# Change this to your own API TOKEN
API_TOKEN = os.environ.get("Lichess-API-Token")

SESSION = berserk.TokenSession(API_TOKEN)

CLIENT = berserk.Client(session=SESSION)

