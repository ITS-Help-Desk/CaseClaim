from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem


class Team(DatabaseItem):
    def __init__(self, role_id: int, color: str, image_url: str, points: int):
        self.role_id = role_id
        self.color = color
        self.image_url = image_url
        self.points = points

    @staticmethod
    def from_role_id(connection: MySQLConnection, role_id: int) -> Optional['Team']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Teams WHERE role_id = %s", (role_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Team(result[0], result[1], result[2], result[3])

    def give_points(self, connection: MySQLConnection, points: int) -> None:
        new_pts = self.points + points
        with connection.cursor() as cursor:
            sql = "UPDATE Teams SET points=%s WHERE role_id = %s"

            cursor.execute(sql, (new_pts, self.role_id,))
            connection.commit()

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Teams (role_id, color, image_url, points) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.role_id, self.color, self.image_url, self.points,))
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
                data.append(Team(result[0], result[1], result[2], result[3]))

            return data

    def export(self) -> list[Any]:
        return [self.role_id, self.color, self.image_url, self.points]
