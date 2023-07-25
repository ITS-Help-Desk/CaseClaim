from typing import Optional
from mysql.connector import MySQLConnection

from bot.models.database_item import DatabaseItem


class User(DatabaseItem):
    def __init__(self, discord_id: int, first_name: str, last_name: str):
        self.discord_id = discord_id

        if first_name.lower() != first_name:
            self.first_name = first_name
        else:
            self.first_name = first_name
        self.last_name = last_name
        self.full_name = first_name + " " + last_name

    @staticmethod
    def from_id(connection: MySQLConnection, discord_id: int) -> Optional['User']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE discord_id = %s", (discord_id, ))
            result = cursor.fetchone()

            if result is None:
                return None

            return User(result[0], result[1], result[2])

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Users (discord_id, first_name, last_name, active) VALUES (%s, %s, %s, %s)"

            cursor.execute(sql, (self.discord_id, self.first_name, self.last_name, True))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Users WHERE discord_id = %s"
            cursor.execute(sql, (self.discord_id,))
            connection.commit()
