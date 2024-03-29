from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem


class Team(DatabaseItem):
    def __init__(self, role_id: int, color: str, image_url: str):
        self.role_id = role_id
        self.color = color
        self.image_url = image_url

    @staticmethod
    def from_role_id(connection: MySQLConnection, role_id: int) -> Optional['Team']:
        """Returns a Team (if found) based on a provided role id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            role_id (int): The id of the role

        Returns:
            Optional[Team] - A representation of the team
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Teams WHERE role_id = %s", (role_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Team(result[0], result[1], result[2])

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Teams (role_id, color, image_url) VALUES (%s, %s, %s)"
            cursor.execute(sql, (self.role_id, self.color, self.image_url,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Teams WHERE role_id = %s"
            cursor.execute(sql, (self.role_id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['Team']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Teams")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(Team(result[0], result[1], result[2]))

            return data
