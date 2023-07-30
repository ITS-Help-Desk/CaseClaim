from abc import ABC, abstractmethod
from mysql.connector import MySQLConnection


class DatabaseItem(ABC):
    @abstractmethod
    def add_to_database(self, connection: MySQLConnection) -> None:
        pass

    @abstractmethod
    def remove_from_database(self, connection: MySQLConnection) -> None:
        pass
