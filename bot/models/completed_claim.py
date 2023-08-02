from datetime import datetime
from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class CompletedClaim(DatabaseItem):
    def __init__(self, checker_message_id: int, case_num: str, tech: User, claim_time: datetime, complete_time: datetime):
        """Creates a representation of a case that's been completed.

        Args:
            checker_message_id (int): The id of the checker message when the case was claimed
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech (User): The user that claimed the case
            claim_time (datetime): The time that the case was claimed
            complete_time (datetime): The time that the case was completed
        """
        self.checker_message_id = checker_message_id
        self.case_num = case_num
        self.tech = tech
        self.claim_time = claim_time
        self.complete_time = complete_time

    @staticmethod
    def from_id(connection: MySQLConnection, checker_message_id: int) -> Optional['CompletedClaim']:
        """Returns a CompletedClaim (if found) based on a provided checker message id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            checker_message_id (int): The id of the checker message when the case was claimed

        Returns:
            Optional[CompletedClaim] - A representation of a completed case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CompletedClaims WHERE checker_message_id = %s", (checker_message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return CompletedClaim(result[0], result[1], User.from_id(connection, result[2]), result[3], result[4])

    @staticmethod
    def get_all_with_tech_id(connection: MySQLConnection, tech_id: int) -> list['CompletedClaim']:
        """Returns a CompletedClaim (if found) based on a provided user id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            tech_id (int): The discord ID of a user

        Returns:
            list[CompletedClaim] - A representation of a completed case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CompletedClaims WHERE tech_id = %s", (tech_id,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CompletedClaim(result[0], result[1], User.from_id(connection, result[2]), result[3], result[4]))

            return data

    @staticmethod
    def get_all_with_case_num(connection: MySQLConnection, case_num: str) -> list['CompletedClaim']:
        """Returns a list of CompletedClaims with a provided case number.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            case_num (str): The case number in Salesforce (e.g. "00960979")

        Returns:
            list[CompletedClaim] - A representation of a completed case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CompletedClaims WHERE case_num = %s", (case_num,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(
                    CompletedClaim(result[0], result[1], User.from_id(connection, result[2]), result[3], result[4]))

            return data

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

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['CompletedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CompletedClaims")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(
                    CompletedClaim(result[0], result[1], User.from_id(connection, result[2]), result[3], result[4]))

            return data

    def export(self) -> list[Any]:
        return [self.checker_message_id, self.case_num, self.tech.discord_id, self.claim_time, self.complete_time]