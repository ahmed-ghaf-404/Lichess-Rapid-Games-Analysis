import pandas as pd
import datetime
from typing import Set

def load_usernames(csv_path: str) -> Set[str]:
    df = pd.read_csv(csv_path)
    return set(df["Username"].astype(str))

def save_usernames(username_set: Set[str], output_dir: str) -> str:
    df = pd.DataFrame({"Username": list(username_set)})
    path = f"{output_dir}/Usernames-{datetime.datetime.now():%Y%m%d-%H%M%S}.csv"
    df.to_csv(path, index=False)
    return path
