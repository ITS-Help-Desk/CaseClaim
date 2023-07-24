from datetime import datetime
from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class CompletedClaim(DatabaseItem):
    def __init__(self, checker_message_id: int, case_num: str, tech: User, claim_time: datetime, complete_time: datetime):
        self.checker_message_id = checker_message_id
        self.case_num = case_num
        self.tech = tech
        self.claim_time = claim_time
        self.complete_time = complete_time

    @staticmethod
    def from_id(connection: MySQLConnection, checker_message_id: int) -> Optional['CompletedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CompletedClaims WHERE checker_message_id = %s", (checker_message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return CompletedClaim(result[0], result[1], User.from_id(connection, result[2]), result[3], result[4])

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO CompletedClaims (checker_message_id, case_num, tech_id, claim_time, complete_time) VALUES (%s, %s, %s, %s, %s)"
            formatted_claim_time = self.claim_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_complete_time = self.complete_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(sql, (self.checker_message_id, self.case_num, self.tech.discord_id, formatted_claim_time, formatted_complete_time,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM CompletedClaims WHERE checker_message_id = %s"
            cursor.execute(sql, (self.checker_message_id,))
            connection.commit()
