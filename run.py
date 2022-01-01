import generate_dataset as gen


if __name__ == "__main__":
    username_set = set()
    username_set.add("ChocoRoku")

    gen.scrape(username_set, "Data")