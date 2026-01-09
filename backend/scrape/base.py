from abc import ABC, abstractmethod
from typing import Iterable

# Abstract class for different implementations
class LichessScraper(ABC):

    # All scrapers will need to fetch games
    @abstractmethod
    def fetch_games(self, username: str) -> Iterable[dict]:
        """
        Yield raw game objects for a user.
        """
        pass
