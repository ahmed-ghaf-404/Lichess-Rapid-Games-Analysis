import _utility as util

def main():
    # testing stuff

    username_csv_file_path = "Data/Prepared_Data/Initial_Usernames.csv"
    username_set = util.getUsernameSet(username_csv_file_path)
    print(len(username_set))
    for username in username_set:
        try:
            util.scrape_n_rapid_games(username,5) 
        except Exception as e:
            continue 
    return


if __name__ == '__main__':
    main()
    