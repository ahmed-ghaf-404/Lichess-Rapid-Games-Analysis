import _utility as util

def main():
    # testing stuff

    username_csv_file_path = "Data/Prepared_Data/Initial_Usernames.csv"
    username_set = util.getUsernameSet(username_csv_file_path)
    print(len(username_set))
    util.scrape_n_rapid_games('adhamsabary',1)
    return


if __name__ == '__main__':
    main()
    