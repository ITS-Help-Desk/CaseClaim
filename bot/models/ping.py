from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem


class Ping(DatabaseItem):
    def __init__(self, thread_id: int, message_id: int, severity: str, description: str):
        self.thread_id = thread_id
        self.message_id = message_id
        self.severity = severity
        self.description = description

    @staticmethod
    def from_thread_id(connection: MySQLConnection, thread_id: int) -> Optional['Ping']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Pings WHERE thread_id = %s", (thread_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Ping(result[0], result[1], result[2], result[3])

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Ping']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Pings WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Ping(result[0], result[1], result[2], result[3])

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Pings (thread_id, message_id, severity, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.thread_id, self.message_id, self.severity, self.description,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Pings WHERE thread_id = %s"
            cursor.execute(sql, (self.thread_id,))
            connection.commit()
