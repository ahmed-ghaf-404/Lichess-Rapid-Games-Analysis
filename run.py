import generate_dataset as Gen
import pandas


if __name__ == "__main__":
    username_set = Gen.read_usernames("Data/Usernames/kaggle_usernames.pkl")

    # username_set = set()
    # username_set.add("ChocoRoku")

    more_usernames = Gen.scrape(username_set, "Data/Games")

    pandas.DataFrame.to_csv(Gen.generate_final_dataset(), "Data/CSV_Files/0.csv")