import time
import json
import subprocess


class SQLBackupCreator:
    def __init__(self, username: str, password: str, database: str, backup_drive_path: str):
        self.username = username
        self.password = password
        self.database = database
        self.backup_drive_path = backup_drive_path

    def create_backup(self) -> str:
        """Creates a local backup of the database using the MySQLDump command in the terminal.

        Returns:
            str - The location of the backup that was generated
        """
        # Create backup
        output = f"backups/{int(time.time())}.sql"
        cmd = f"mysqldump -u {self.username} -p\"{self.password}\" {self.database} > {output}"
        s = subprocess.Popen(cmd, shell=True)
        s.wait()

        # Copy backup to drive (currently disabled)
        '''new_output = output.replace("/", "\\")
        new_output = output
        cmd1 = f"cp {new_output} {self.backup_drive_path}"
        print(cmd1)
        subprocess.Popen(cmd1, shell=True)'''

        return output


if __name__ == "__main__":
    with open("config.json", "r") as f:
        data = json.load(f)
        user = data["db_user"]
        passwrd = data["db_password"]
        name = data["db_name"]
        drive_backup_path = data["drive_backup_path"]

    b = SQLBackupCreator(user, passwrd, name, drive_backup_path)
    while True:
        try:
            f = b.create_backup()
        except Exception as e:
            print(e)
        time.sleep(86400)  # Once every day
