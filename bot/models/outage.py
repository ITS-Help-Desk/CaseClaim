from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem
from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


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
            cursor.execute("SELECT * FROM Outages WHERE case_message_id = %s", (message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return Outage(result[0], result[1], result[2], result[3], result[4], result[5], result[6], User.from_id(connection, result[7]), bool(result[8]))

    @staticmethod
    async def resend(bot):
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
