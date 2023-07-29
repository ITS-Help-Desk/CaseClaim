from mysql.connector import MySQLConnection
from typing import Optional
from datetime import datetime

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class Announcement(DatabaseItem):
    def __init__(self, message_id: int, case_message_id: int, title: str, description: str, user: User, end_time: datetime, active: bool):
        """Creates an object representation of a server announcement.

        Args:
            message_id (int): The ID of the announcement message
            case_message_id (int): The ID of the case message
            title (str): The title of the announcement
            description (str): The description of the announcement
            user (User): The user that sent the announcement
            end_time (datetime): The date that the announcement will be deleted
            active (bool): Whether or not the announcement is active
        """
        self.message_id = message_id
        self.case_message_id = case_message_id
        self.title = title
        self.description = description
        self.user = user
        self.end_time = end_time
        self.active = active

    @staticmethod
    def from_message_id(connection: MySQLConnection, message_id: int) -> Optional['Announcement']:
        """Returns an announcement (if found) with the matching message ID

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The announcement message ID

        Returns:
            Optional[Announcement] - The announcement that matches with the provided message ID
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Announcement(result[0], result[1], result[2], result[3], User.from_id(connection, result[4]), result[5], bool(result[6]))

    @staticmethod
    def from_case_message_id(connection: MySQLConnection, message_id: int) -> Optional['Announcement']:
        """Returns an announcement (if found) with the matching case message ID

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            message_id (int): The case channel message ID

        Returns:
            Optional[Announcement] - The announcement that matches with the provided case message ID
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE case_message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Announcement(result[0], result[1], result[2], result[3], User.from_id(connection, result[4]), result[5], bool(result[6]))

    @staticmethod
    async def resend(bot):
        """Deletes any announcements that have expired and edits the announcement message to show that
        the announcement is no longer active.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        with bot.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE active = 1")
            results = cursor.fetchall()

            for result in results:
                ann = Announcement(result[0], result[1], result[2], result[3], User.from_id(bot.connection, result[4]), result[5], result[6])

                if ann.end_time < datetime.now():
                    # Edit announcement message
                    announcement_channel = await bot.fetch_channel(bot.announcement_channel)
                    announcement_message = await announcement_channel.fetch_message(ann.message_id)

                    announcement_embed = announcement_message.embeds[0]
                    announcement_embed.colour = bot.embed_color
                    await announcement_message.edit(content="", embed=announcement_embed)

                    # Delete case message
                    case_channel = await bot.fetch_channel(bot.cases_channel)
                    case_message = await case_channel.fetch_message(ann.case_message_id)
                    await case_message.delete()

                    ann.deactivate(bot.connection)

    def deactivate(self, connection: MySQLConnection) -> None:
        """Deactivates the announcement so that it no longer appears in MySQL queries.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
        """
        with connection.cursor() as cursor:
            sql = f"UPDATE Announcements SET active=0 WHERE message_id={self.message_id}"
            cursor.execute(sql)
            connection.commit()

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
