from mysql.connector import MySQLConnection
from datetime import datetime

from bot.models.database_item import DatabaseItem


class TeamPoint(DatabaseItem):
    def __init__(self, id: int, role_id: int, points: int, description: str, timestamp: datetime):
        """Creates a TeamPoint object to store data such as points and description.

        Args:
            id (int): An auto incrementing int id
            role_id (int): The id of the team that is being awarded
            points (int): The amount of points to be awarded (1-5)
            description (str): The reason for the award
            timestamp (datetime): The time of the award
        """
        self.id = id
        self.role_id = role_id
        self.points = points
        self.description = description
        self.timestamp = timestamp

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO TeamPoints (role_id, points, description, timestamp) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.role_id, self.points, self.description, self.timestamp,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM TeamPoints WHERE id = %s"
            cursor.execute(sql, (self.id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['TeamPoint']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM TeamPoints")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(TeamPoint(result[0], result[1], result[2], result[3], result[4]))

            return data
