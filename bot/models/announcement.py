from mysql.connector import MySQLConnection
from typing import Optional
from datetime import datetime

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class Announcement(DatabaseItem):
    def __init__(self, message_id: int, case_message_id: int, title: str, description: str, user: User, end_time: datetime, active: bool):
        self.message_id = message_id
        self.case_message_id = case_message_id
        self.title = title
        self.description = description
        self.user = user
        self.end_time = end_time
        self.active = active

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Announcement']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Announcement(result[0], result[1], result[2], result[3], User.from_id(connection, result[4]), result[5], bool(result[6]))

    @staticmethod
    def from_case_message_id(connection: MySQLConnection, message_id: int) -> Optional['Announcement']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE case_message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Announcement(result[0], result[1], result[2], result[3], User.from_id(connection, result[4]), result[5], bool(result[6]))

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Announcements (message_id, case_message_id, title, description, user, end_time, active) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.message_id, self.case_message_id, self.title, self.description, self.user.discord_id, self.end_time, self.active,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Announcements WHERE message_id = %s"
            cursor.execute(sql, (self.message_id,))
            connection.commit()
