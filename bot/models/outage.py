from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class Outage(DatabaseItem):
    def __init__(self, message_id: int, case_message_id: int, service: str, parent_case: Optional[str], description: str, troubleshooting_steps: Optional[str], resolution_time: Optional[str], user: User, active: bool):
        self.message_id = message_id
        self.case_message_id = case_message_id
        self.service = service
        self.parent_case = parent_case
        self.description = description
        self.troubleshooting_steps = troubleshooting_steps
        self.resolution_time = resolution_time
        self.user = user
        self.active = active

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Outage']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Outages WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6], User.from_id(connection, result[7]), bool(result[8]))

    @staticmethod
    def from_case_message_id(connection: MySQLConnection, message_id: int) -> Optional['Outage']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE case_message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6], User.from_id(connection, result[7]), bool(result[8]))

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Outages (message_id, case_message_id, service, parent_case, description, troubleshooting_steps, resolution_time, user, active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.message_id, self.case_message_id, self.service, self.parent_case, self.description, self.troubleshooting_steps, self.resolution_time, self.user.discord_id, self.active,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Outages WHERE message_id = %s"
            cursor.execute(sql, (self.message_id,))
            connection.commit()
