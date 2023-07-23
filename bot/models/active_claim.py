from datetime import datetime
from mysql.connector import MySQLConnection
from typing import Optional

from database_item import DatabaseItem
from user import User


class ActiveClaim(DatabaseItem):
    def __init__(self, claim_message_id: int, case_num: str, tech: User, claim_time: datetime):
        self.claim_message_id = claim_message_id
        self.case_num = case_num
        self.tech = tech
        self.claim_time = claim_time

    @staticmethod
    def from_id(connection: MySQLConnection, claim_message_id: int) -> Optional['ActiveClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE claim_message_id = %s", (claim_message_id,))
            result = cursor.fetchone()

            return ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3])

    @staticmethod
    def from_case_num(connection: MySQLConnection, case_num: str) -> Optional['ActiveClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE case_num = %s", (case_num,))
            result = cursor.fetchone()

            return ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3])

    def add_to_database(self) -> None:
        pass

    def remove_from_database(self) -> None:
        pass
