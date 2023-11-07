from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem


class PendingPing(DatabaseItem):
    def __init__(self, checker_message_id: int, severity: str, description: str, to_do: str):
        """Creates a Ping object to store data such as severity and description.

        Args:
            checker_message_id (int): The id of the checker message
            severity (str): The severity of the ping
            description (str): The description of the ping
            to_do (str): The instructions for the tech
        """
        self.checker_message_id = checker_message_id
        self.severity = severity
        self.description = description
        self.to_do = to_do

    @staticmethod
    def from_checker_message_id(connection: MySQLConnection, checker_message_id: int) -> Optional['PendingPing']:
        """Returns a PendingPing (if found) based on a provided checker message id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            checker_message_id (int): The id of the thread

        Returns:
            Optional[PendingPing] - A representation of a ping
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM PendingPings WHERE checker_message_id = %s", (checker_message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return PendingPing(result[0], result[1], result[2], result[3])

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO PendingPings (checker_message_id, severity, description, `to_do`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.checker_message_id, self.severity, self.description, self.to_do,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM PendingPings WHERE checker_message_id = %s"
            cursor.execute(sql, (self.checker_message_id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['PendingPing']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM PendingPings")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(PendingPing(result[0], result[1], result[2], result[3]))

            return data
