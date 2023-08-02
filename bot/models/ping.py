from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem


class Ping(DatabaseItem):
    def __init__(self, thread_id: int, message_id: int, severity: str, description: str):
        """

        Args:
            thread_id (int): The id of the thread that was created when the ping was sent
            message_id (int): The id of the message that contains the ping information
            severity (str): The severity of the ping
            description (str): The description of the ping
        """
        self.thread_id = thread_id
        self.message_id = message_id
        self.severity = severity
        self.description = description

    @staticmethod
    def from_thread_id(connection: MySQLConnection, thread_id: int) -> Optional['Ping']:
        """Returns a Ping (if found) based on a provided thread id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            thread_id (int): The id of the thread

        Returns:
            Optional[Ping] - A representation of a ping
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Pings WHERE thread_id = %s", (thread_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Ping(result[0], result[1], result[2], result[3])

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Ping']:
        """Returns a Ping (if found) based on a provided message id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The id of the message containing the ping information

        Returns:
            Optional[Ping] - A representation of a ping
        """
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

    def export(self) -> list[Any]:
        return [self.thread_id, self.message_id, self.severity, self.description]
