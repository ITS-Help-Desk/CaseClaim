import time
import json
import subprocess


class SQLBackupCreator:
    def __init__(self, username: str, password: str, database: str):
        self.username = username
        self.password = password
        self.database = database

    def create_backup(self) -> str:
        """Creates a local backup of the database using the MySQLDump command.

        Returns:
            str - The location of the backup that was generated
        """
        mac_cmd = "/usr/local/mysql-8.0.31-macos12-arm64/bin/mysqldump"
        output = f"backups/{int(time.time())}.sql"
        cmd = f"mysqldump -u {self.username} -p\"{self.password}\" {self.database} > {output}"
        subprocess.Popen(cmd, shell=True)

        return output


if __name__ == "__main__":
    with open("config.json", "r") as f:
        data = json.load(f)
        user = data["db_user"]
        passwrd = data["db_password"]
        name = data["db_name"]

    b = SQLBackupCreator(user, passwrd, name)
    while True:
        try:
            f = b.create_backup()
        except Exception as e:
            print(e)
        time.sleep(86400)  # Once every day
