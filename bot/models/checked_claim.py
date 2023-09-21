from datetime import datetime

from mysql.connector import MySQLConnection
from typing import Optional, Any

from bot.models.database_item import DatabaseItem
from bot.models.user import User

from bot.status import Status


class CheckedClaim(DatabaseItem):
    def __init__(self, checker_message_id: int, case_num: str, tech: User, lead: User, claim_time: datetime,
                 complete_time: datetime, check_time: datetime, status: Status, ping_thread_id: Optional[int]):
        """Creates a representation of a case that's been checked by a lead.

        Args:
            checker_message_id (int): The id of the checker message when the case was claimed
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech (User): The user that claimed the case
            lead (User): The user that checked the case
            claim_time (datetime): The time that the case was claimed
            complete_time (datetime): The time that the case was completed
            check_time (datetime): The time that the case was checked
            status (Status): The status of the case (e.g. Checked, Pinged, Resolved, etc)
            ping_thread_id (Optional[int]): The ID of the Ping thread
        """
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
        """Returns a CheckedClaim (if found) based on a ping thread id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            ping_thread_id (int): The ID of the ping thread

        Returns:
            Optional[CheckedClaim] - A representation of a checked case
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE ping_thread_id = %s", (ping_thread_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                User.from_id(connection, result[3]),
                                result[4], result[5], result[6], Status.from_str(result[7]), result[8])

    @staticmethod
    def get_all_with_tech_id(connection: MySQLConnection, tech_id: int) -> list['CheckedClaim']:
        """Returns a list of CheckedClaim based on a tech id.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            tech_id (int): The discord ID of the tech

        Returns:
            list[CheckedClaim] - A list of checked cases
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE tech_id = %s", (tech_id,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data

    @staticmethod
    def get_all_with_case_num(connection: MySQLConnection, case_num: str) -> list['CheckedClaim']:
        """Returns a list of CheckedClaim based on a case number.
        
        Args:
            connection (MySQLConnection): The connection to the MySQL database
            case_num (str): The case number in Salesforce (e.g. "00960979")

        Returns:
            list[CheckedClaim] - A list of checked cases
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE case_num = %s", (case_num,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data

    def add_ping_thread(self, connection: MySQLConnection, ping_thread_id: int) -> None:
        """Updates the database to include a provided ping thread ID.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            ping_thread_id (int): The ID of the ping thread created
        """
        with connection.cursor() as cursor:
            sql = "UPDATE CheckedClaims SET ping_thread_id=%s WHERE checker_message_id=%s"
            cursor.execute(sql, (ping_thread_id, self.checker_message_id,))
            connection.commit()

    def change_status(self, connection: MySQLConnection, new_status: Status):
        """Changes the status of a CheckedClaim in the database
        
        Args:
            connection (MySQLConnection): The connection to the MySQL database 
            new_status (Status): The new status that the CheckedClaim will have
        """
        with connection.cursor() as cursor:
            if new_status == Status.CHECKED:
                sql = "UPDATE CheckedClaims SET ping_thread_id = %s WHERE checker_message_id=%s"
                cursor.execute(sql, (None, self.checker_message_id,))

            sql = "UPDATE CheckedClaims SET status = %s WHERE checker_message_id=%s"
            cursor.execute(sql, (new_status, self.checker_message_id,))
            connection.commit()

    @staticmethod
    def search(connection: MySQLConnection, user: Optional[User] = None, month: Optional[int] = None, status: Status = None) -> list['CheckedClaim']:
        """Searches the list of CheckedClaims based on the specified parameters.
        
        Args:
            connection (MySQLConnection): The connection to the MySQL database 
            user (Optional[User]): The user that worked on the CheckedClaim
            month (Optional[int]): The month that the CheckedClaim was claimed in
            status (Status): The status of the case

        Returns:
            list[CheckedClaim] - A list of CheckedClaims matching the parameters
        """
        sql = "SELECT * FROM CheckedClaims WHERE 1=1"

        if user is not None:
            sql += f" AND tech_id = {user.discord_id}"

        if month is not None:
            now = datetime.now()
            beginning = f"'{now.year}-{month}-1 00:00:00'"

            match month:
                case 1 | 3 | 5 | 7 | 8 | 10 | 12:
                    end = 31
                case 4 | 6 | 9 | 11:
                    end = 30
                case 2:
                    end = 28
            ending = f"'{now.year}-{month}-{end} 23:59:59'"
            sql += f" AND claim_time BETWEEN {beginning} AND {ending}"

        if status is not None:
            if status == Status.PINGED or status == Status.RESOLVED:
                sql += f" AND (`status` = '{status}' OR `status` = '{Status.RESOLVED}'"
            else:
                sql += f" AND `status` = '{status}'"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()

            data = []
            for result in results:
                if result[1] == '12341234':
                    continue
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))
            return data

    @staticmethod
    def find_latest_case(connection: MySQLConnection, user: User, case_num: str) -> Optional['CheckedClaim']:
        """Finds the latest non-pinged case from the user with the case_num provided.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            user (User): The tech responsible for the case
            case_num (str): The case number in Salesforce

        Returns:
            Optional[CheckedClaim] - The CheckedClaim (if it can be found)
        """
        with connection.cursor() as cursor:
            sql = "SELECT * FROM CheckedClaims WHERE tech_id=%s AND case_num=%s AND status != %s"
            cursor.execute(sql, (user.discord_id, case_num, Status.PINGED,))
            result = cursor.fetchone()

            if result is not None and len(result) != 0:
                return CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                    User.from_id(connection, result[3]),
                                    result[4], result[5], result[6], Status.from_str(result[7]), result[8])
            else:
                return None

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO CheckedClaims (checker_message_id, case_num, tech_id, lead_id, claim_time, complete_time, check_time, status, ping_thread_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            formatted_claim_time = self.claim_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_complete_time = self.complete_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_check_time = self.check_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(sql, (
            self.checker_message_id, self.case_num, self.tech.discord_id, self.lead.discord_id, formatted_claim_time,
            formatted_complete_time, formatted_check_time, self.status, self.ping_thread_id))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM CheckedClaims WHERE checker_message_id = %s"
            cursor.execute(sql, (self.checker_message_id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['CheckedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims")
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data

    @staticmethod
    def get_all_leaderboard(connection: MySQLConnection, year: int) -> list['CheckedClaim']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CheckedClaims WHERE status != %s AND YEAR(claim_time) = %s AND case_num != '12341234'", (str(Status.DONE), year,))
            results = cursor.fetchall()

            data = []
            for result in results:
                data.append(CheckedClaim(result[0], result[1], User.from_id(connection, result[2]),
                                         User.from_id(connection, result[3]),
                                         result[4], result[5], result[6], Status.from_str(result[7]), result[8]))

            return data
