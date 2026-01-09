import berserk
import os
from dotenv import load_dotenv

from backend.constant import BERSERK_ACCESS_TOKEN

def get_client():
    load_dotenv() 
    token = os.getenv(BERSERK_ACCESS_TOKEN)

    if not token:
        raise RuntimeError(
            f"Environment variable '{BERSERK_ACCESS_TOKEN}' is not set"
        )

    session = berserk.TokenSession(token)
    return berserk.Client(session=session)