import time
import _utility as util
from DatabaseManager import DatabaseManager


def main():
    # start the application
    print("Welcome to Lichess Rapid Games Analysis.")

    # connect to Database
    dbManager = DatabaseManager()

    choice = input(
        """Main Menu:
        1 Database stats
    """
    )

    match choice:
        case "1":
            dbManager.countQuery()

    # testing stuff
    username_csv_file_path = "Data/Prepared_Data/Initial_Usernames.csv"

    isEdit = input(
        f"Current data path is {username_csv_file_path}\nPress E to edit"
    )
    if isEdit.lower() == "e":
        while isEdit.lower() == "e":
            isEdit = input(
                f"Current data path is {username_csv_file_path}\nPress E to edit"
            )

    username_set = util.getUsernameSet(username_csv_file_path)
    count = 0
    for username in username_set:
        try:
            util.scrape_n_rapid_games(username, 5)
        except Exception as e:
            continue
        count += 1
        if count == 10:
            time.sleep(1)
            count = 0

    util.buildDataset("Data/Scraped_Files")

    dbManager.closeDatabase()
    return


if __name__ == "__main__":
    main()
