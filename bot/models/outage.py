from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem
from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class Outage(DatabaseItem):
    def __init__(self, message_id: int, case_message_id: int, service: str, parent_case: Optional[str], description: str, troubleshooting_steps: Optional[str], resolution_time: Optional[str], user: User, active: bool):
        """

        Args:
            message_id (int): The ID of the announcement message
            case_message_id (int): The ID of the case message
            service (str): The name of the service being affected
            parent_case (Optional[str]): The parent case number of the outage
            description (str): The description of the outage
            troubleshooting_steps (Optional[str]): The troubleshooting steps of the outage
            resolution_time (Optional[str]): The resolution time of the outage
            user (User): The user that sent the outage
            active (bool): Whether or not the outage is active
        """
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
        """Returns an outage (if found) with the matching message ID

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The announcment message ID

        Returns:
            Optional[Outage] - The outage that matches the message id
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Outages WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6], User.from_id(connection, result[7]), bool(result[8]))

    @staticmethod
    def from_case_message_id(connection: MySQLConnection, message_id: int) -> Optional['Outage']:
        """Returns an outage (if found) with the matching case message ID

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The case message ID

        Returns:
            Optional[Outage] - The outage that matches with the provided case message id
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Outages WHERE case_message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6], User.from_id(connection, result[7]), bool(result[8]))

    @staticmethod
    async def resend(bot):
        """Deletes and resends the outage to the cases discord channel

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        with bot.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Outages WHERE active = 1")
            results = cursor.fetchall()

            for result in results:
                outage = Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6],
                                User.from_id(bot.connection, result[7]), bool(result[8]))

                case_channel = await bot.fetch_channel(bot.cases_channel)
                case_message = await case_channel.fetch_message(outage.case_message_id)

                new_message = await case_channel.send(embed=case_message.embeds[0],
                                                      silent=True)
                cursor.execute(f"UPDATE Outages SET case_message_id={new_message.id} WHERE message_id={outage.message_id}")
                bot.connection.commit()
                await case_message.delete()

    def deactivate(self, connection: MySQLConnection) -> None:
        """Deactivates the outage so that it no longer appears in MySQL queries.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
        """
        with connection.cursor() as cursor:
            sql = f"UPDATE Outages SET active=0 WHERE message_id={self.message_id}"
            cursor.execute(sql)
            connection.commit()

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

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['Outage']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Outages")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6],
                            User.from_id(connection, result[7]), bool(result[8])))
            return data
