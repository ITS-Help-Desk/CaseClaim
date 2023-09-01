from typing import Optional, Any
from mysql.connector import MySQLConnection

from bot.models.team import Team
from bot.models.database_item import DatabaseItem


class User(DatabaseItem):
    def __init__(self, discord_id: int, first_name: str, last_name: str, team_id: Optional[int]):
        """Creates a representation of a user

        Args:
            discord_id (int): The discord ID of a user
            first_name (str): The first name of a user
            last_name (str): The last name of a user
            team_id (Optional[int]): The ID of the user's team
        """
        self.discord_id = discord_id
        self.team_id = team_id

        if first_name[0].isupper():
            self.first_name = first_name
        else:
            self.first_name = first_name.capitalize()

        if last_name[0].isupper():
            self.last_name = last_name
        else:
            self.last_name = last_name.capitalize()

        self.full_name = first_name + " " + last_name

    @staticmethod
    def from_id(connection: MySQLConnection, discord_id: int) -> Optional['User']:
        """Returns a User (if found) based on a provided discord ID

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            discord_id (int): The discord ID of a user

        Returns:
            Optional[User] - A representation of a user
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE discord_id = %s", (discord_id, ))
            result = cursor.fetchone()

            if result is None:
                return None

            return User(result[0], result[1], result[2], result[3])

    def add_team(self, connection: MySQLConnection, team: Team):
        """Adds a team to a user's row in the Users table.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            team (Team): The new team to add to the user
        """
        with connection.cursor() as cursor:
            sql = "UPDATE Users SET team=%s WHERE discord_id = %s"

            cursor.execute(sql, (team.role_id, self.discord_id,))
            connection.commit()

    def edit_name(self, connection: MySQLConnection, new_first: str, new_last: str):
        """Edit a user's first and last name in the User's table. This is used
        if a user types the /join command after they've already joined.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            new_first (str): The user's new first name
            new_last (str): The user's new last name
        """
        with connection.cursor() as cursor:
            sql = "UPDATE Users SET first_name=%s, last_name=%s WHERE discord_id = %s"

            cursor.execute(sql, (new_first, new_last, self.discord_id,))
            connection.commit()

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Users (discord_id, first_name, last_name, team) VALUES (%s, %s, %s, %s)"

            cursor.execute(sql, (self.discord_id, self.first_name, self.last_name, self.team_id))
            connection.commit()

    def remove_from_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Users WHERE discord_id = %s"
            cursor.execute(sql, (self.discord_id,))
            connection.commit()

    @staticmethod
    def get_all(connection: MySQLConnection) -> list['User']:
        """Gets all the users in the database

        Args:
            connection (MySQLConnection): The connection to the MySQL database

        Returns:
            list[User] - A list of users
        """
        with connection.cursor() as cursor:
            users = []
            cursor.execute("SELECT * FROM Users")
            results = cursor.fetchall()

            for result in results:
                users.append(User(result[0], result[1], result[2], result[3]))

            return users
