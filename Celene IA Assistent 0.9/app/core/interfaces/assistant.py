from abc import ABC, abstractmethod


class Assistant(ABC):

    @abstractmethod
    def think(self, message: str) -> str:
        pass