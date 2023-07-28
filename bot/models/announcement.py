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

    @staticmethod
    async def resend(bot):
        with bot.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Announcements WHERE active = 1")
            results = cursor.fetchall()

            for result in results:
                ann = Announcement(result[0], result[1], result[2], result[3], User.from_id(bot.connection, result[4]), result[5], result[6])

                if ann.end_time < datetime.now():
                    announcement_channel = await bot.fetch_channel(bot.announcement_channel)
                    announcement_message = await announcement_channel.fetch_message(ann.message_id)

                    announcement_embed = announcement_message.embeds[0]
                    announcement_embed.colour = bot.embed_color
                    await announcement_message.edit(content="", embed=announcement_embed)

                    case_channel = await bot.fetch_channel(bot.cases_channel)
                    case_message = await case_channel.fetch_message(ann.case_message_id)
                    await case_message.delete()

                    ann.deactivate(bot.connection)

    def deactivate(self, connection: MySQLConnection) -> None:
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
