from typing import Optional
from mysql.connector import MySQLConnection

from database_item import DatabaseItem


class User(DatabaseItem):
    def __init__(self, discord_id: int, first_name: str, last_name: str):
        self.discord_id = discord_id
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def from_id(connection: MySQLConnection, discord_id: int) -> Optional['User']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE discord_id = %s", (discord_id, ))
            result = cursor.fetchone()

            return User(result[0], result[1], result[2])

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def add_to_database(self) -> None:
        pass

    def remove_from_database(self) -> None:
        pass
