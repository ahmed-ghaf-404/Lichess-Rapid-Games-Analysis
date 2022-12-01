# Chess-Level-Guesser
## DEPENDENCIES:
- [pandas](https://pandas.pydata.org/docs/getting_started/install.html): {brief explanation}
- [berserk](https://github.com/rhgrant10/berserk): {brief explanation}
- [NumPy](https://numpy.org/install/): {brief explanation}
- [Seaborn](https://seaborn.pydata.org/): {brief explanation}

See also 
- [lichess](https://lichess.org/about) is a free/libre, open-source chess server powered by volunteers and donations created in 2010.
- [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system) is the rating system used in online chess and FIDE.

## Problem
Although chess is ancient, it was not until recently chess was analyzed by computers and by data. Most current online chess website, like \href{lichess.org/about}{lichess}, provide analysis tools for its patrons and casual players. With such option available to users, the question of "can we use online chess game analysis to determine the level of a chess player?" arose to my mind. The question cannot be answered easily since all the required data is not available publicly for every-day users and many intermediate tasks must be done before then.

## Tasks Overview
Due to the lack of data, I used an open-source API to scrape data from online chess games. After obtaining many raw and meaningless data, I cleaned, processed, and stored the data in a postgresSQL. Being able to add and load new game data helped raising the integrity of data (cheating, uneven match-ups, casual games, etc...). Then, I analyzed all the level-dependent variables, such as how good each move played was, and attempted to find noticeable trends in data. Chess game data throughout the 3 skill-levels of the game are clustered very closely, which make it hard to differentiate, so I spread the data by multiplying by an offset value.
~~readme writing progress~~
