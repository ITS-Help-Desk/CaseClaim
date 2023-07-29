from datetime import datetime
from mysql.connector import MySQLConnection
from typing import Optional

from bot.models.database_item import DatabaseItem
from bot.models.user import User


class ActiveClaim(DatabaseItem):
    def __init__(self, claim_message_id: int, case_num: str, tech: User, claim_time: datetime):
        """Creates a representation of a case that's actively being worked on.

        Args:
            claim_message_id (int): The id of the message when the case was claimed
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech (User): The user that claimed the case
            claim_time (datetime): The time that the case was claimed
        """
        self.claim_message_id = claim_message_id
        self.case_num = case_num
        self.tech = tech
        self.claim_time = claim_time

    @staticmethod
    def from_id(connection: MySQLConnection, claim_message_id: int) -> Optional['ActiveClaim']:
        """Returns an ActiveClaim (if found) based on a provided claim message id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            claim_message_id (claim_message_id): The id of the message when the case was claimed

        Returns:
            ActiveClaim - A representation of the actively claimed case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE claim_message_id = %s", (claim_message_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3])

    @staticmethod
    def from_case_num(connection: MySQLConnection, case_num: str) -> Optional['ActiveClaim']:
        """Returns an ActiveClaim (if found) based on a provided case number

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            case_num (str): The case number in Salesforce (e.g. "00960979")

        Returns:
            ActiveClaim - A representation of the actively claimed case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE case_num = %s", (case_num,))
            result = cursor.fetchone()

            if result is None:
                return None

            return ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3])

    @staticmethod
    def get_all_with_tech_id(connection: MySQLConnection, tech_id: int) -> list['ActiveClaim']:
        """Returns a list of ActiveClaim that a tech is working on.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            tech_id (int): The tech's discord ID number

        Returns:
            list[ActiveClaim] - A list of all claims that a tech is working on.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE tech_id = %s", (tech_id,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3]))

            return data

    @staticmethod
    def get_all_with_case_num(connection: MySQLConnection, case_num: str) -> list['ActiveClaim']:
        """Finds all cases with the provided case number and returns the list of them.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            case_num (str): The case number in Salesforce (e.g. "00960979")

        Returns:
            list[ActiveClaim] - A list of all claims with the same case number
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ActiveClaims WHERE case_num = %s", (case_num,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(ActiveClaim(result[0], result[1], User.from_id(connection, result[2]), result[3]))

            return data

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO ActiveClaims (claim_message_id, case_num, tech_id, claim_time) VALUES (%s, %s, %s, %s)"
            formatted_date = self.claim_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(sql, (self.claim_message_id, self.case_num, self.tech.discord_id, formatted_date,))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM ActiveClaims WHERE claim_message_id = %s"
            cursor.execute(sql, (self.claim_message_id,))
            connection.commit()
