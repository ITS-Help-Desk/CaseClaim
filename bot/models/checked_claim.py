from datetime import datetime
from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem
from bot.models.user import User

from bot.status import Status


class CheckedClaim(DatabaseItem):
    def __init__(self, checker_message_id: int, case_num: str, tech: User, lead: User, claim_time: datetime,
                 complete_time: datetime, check_time: datetime, status: Status, ping_thread_id: Optional[int]):
        self.checker_message_id = checker_message_id
        self.case_num = case_num

        self.tech = tech
        self.lead = lead

        self.claim_time = claim_time
        self.complete_time = complete_time
        self.check_time = check_time

        self.status = status
        self.ping_thread_id = ping_thread_id

    @staticmethod
    def from_ping_thread_id(connection: MySQLConnection, ping_thread_id: int) -> Optional['CheckedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE ping_thread_id = %s", (ping_thread_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return CheckedClaim(result[0], result[1], User.from_id(connection, result[2]), User.from_id(connection, result[3]),
                                result[4], result[5], result[6], Status.from_str(result[7]), result[8])

    @staticmethod
    def get_all_with_tech_id(connection: MySQLConnection, tech_id: int) -> list['CheckedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE tech_id = %s", (tech_id,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]), User.from_id(connection, result[3]),
                            result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data

    @staticmethod
    def get_all_with_case_num(connection: MySQLConnection, case_num: str) -> list['CheckedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE case_num = %s", (case_num,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data

    def change_status(self, connection: MySQLConnection, new_status: Status):
        with connection.cursor() as cursor:
            if new_status == Status.CHECKED:
                sql = "UPDATE CheckedClaims SET ping_thread_id = %s WHERE checker_message_id=%s"
                cursor.execute(sql, (None, self.checker_message_id,))

            sql = "UPDATE CheckedClaims SET status = %s WHERE checker_message_id=%s"
            cursor.execute(sql, (new_status, self.checker_message_id,))
            connection.commit()

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO CheckedClaims (checker_message_id, case_num, tech_id, lead_id, claim_time, complete_time, check_time, status, ping_thread_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            formatted_claim_time = self.claim_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_complete_time = self.complete_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_check_time = self.check_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(sql, (self.checker_message_id, self.case_num, self.tech.discord_id, self.lead.discord_id, formatted_claim_time,
                                 formatted_complete_time, formatted_check_time, self.status, self.ping_thread_id))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM CheckedClaims WHERE checker_message_id = %s"
            cursor.execute(sql, (self.checker_message_id,))
            connection.commit()
