from abc import ABC, abstractmethod


class DatabaseItem(ABC):
    @abstractmethod
    def add_to_database(self) -> None:
        pass

    @abstractmethod
    def remove_from_database(self) -> None:
        pass
