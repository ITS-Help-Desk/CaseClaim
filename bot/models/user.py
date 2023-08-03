from typing import Optional, Any
from mysql.connector import MySQLConnection

from bot.models.database_item import DatabaseItem


class User(DatabaseItem):
    def __init__(self, discord_id: int, first_name: str, last_name: str, team: int, active: bool):
        """Creates a representation of a user

        Args:
            discord_id (int): The discord ID of a user
            first_name (str): The first name of a user
            last_name (str): The last name of a user
        """
        self.discord_id = discord_id
        self.team = team
        self.active = active

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

            return User(result[0], result[1], result[2], int(result[3]), bool(result[4]))

    def add_team(self, connection: MySQLConnection, new_team_id: int):
        """Adds a team to a user's row in the Users table.

        Args:
            connection (MySQLConnection): The connection to the MySQL database
            new_team_id (int): The ID of the new team that they'll be placed in
        """
        with connection.cursor() as cursor:
            sql = "UPDATE Users SET team=%s WHERE discord_id = %s"

            cursor.execute(sql, (new_team_id, self.discord_id,))
            connection.commit()

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def add_to_database(self, connection: MySQLConnection) -> None:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Users (discord_id, first_name, last_name, team, active) VALUES (%s, %s, %s, %s, %s)"

            cursor.execute(sql, (self.discord_id, self.first_name, self.last_name, self.team, self.active))
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
                users.append(User(result[0], result[1], result[2], int(result[3]), bool(result[4])))

            return users

    def export(self) -> list[Any]:
        return [self.discord_id, self.first_name, self.last_name, self.team, self.active]
