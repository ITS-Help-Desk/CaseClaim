from abc import ABC, abstractmethod
from mysql.connector import MySQLConnection
from typing import Any


class DatabaseItem(ABC):
    @abstractmethod
    def add_to_database(self, connection: MySQLConnection) -> None:
        pass

    @abstractmethod
    def remove_from_database(self, connection: MySQLConnection) -> None:
        pass

    @staticmethod
    @abstractmethod
    def get_all(connection: MySQLConnection) -> list['DatabaseItem']:
        pass

    @abstractmethod
    def export(self) -> list[Any]:
        pass
