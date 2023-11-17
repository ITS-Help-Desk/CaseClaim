from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem


class Feedback(DatabaseItem):
    def __init__(self, thread_id: int, message_id: int, severity: str, description: str):
        """Creates a Feedback object to store data such as severity and description.

        Args:
            thread_id (int): The id of the thread that was created when the ping/kudo was sent
            message_id (int): The id of the message that contains the ping/kudo information
            severity (str): The severity of the ping/kudo
            description (str): The description of the ping/kudo
        """
        self.thread_id = thread_id
        self.message_id = message_id
        self.severity = severity
        self.description = description

    @staticmethod
    def from_thread_id(connection: MySQLConnection, thread_id: int) -> Optional['Feedback']:
        """Returns a Ping/kudo (if found) based on a provided thread id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            thread_id (int): The id of the thread

        Returns:
            Optional[Feedback] - A representation of a ping/kudo
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Feedback WHERE thread_id = %s", (thread_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Feedback(result[0], result[1], result[2], result[3])

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Feedback']:
        """Returns a Ping (if found) based on a provided message id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The id of the message containing the ping information

        Returns:
            Optional[Ping] - A representation of a ping
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Feedback WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Feedback(result[0], result[1], result[2], result[3])

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Feedback (thread_id, message_id, severity, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.thread_id, self.message_id, self.severity, self.description,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Feedback WHERE thread_id = %s"
            cursor.execute(sql, (self.thread_id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['Feedback']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Feedback")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(Feedback(result[0], result[1], result[2], result[3]))

            return data
