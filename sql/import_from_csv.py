"""Place this file in the same folder as the CSV files and run in order
to load the MySQL tables with data from the CSV files.
"""

import csv
import mysql.connector
from mysql.connector import Error


# Get database login information
user = input("DB user: ")
password = input("DB password: ")
host = input("DB host: ")
database = input("DB name: ")

db_config = {
    'user': user,
    'password': password,
    'host': host,
    'database': database,
    'raise_on_warnings': True
}

connection = None
try:
    connection = mysql.connector.connect(**db_config)
    print("MySQL Database connection successful\n")
except Error as err:
    print(f"Error: '{err}'")

file_names = ["users", "pings", "activeclaims", "announcements", "checkedclaims", "completedclaims", "outages"]


# Go through each file and add to the database
for file in file_names:
    with open(f"{file}.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)

        with connection.cursor() as cursor:
            for row in csv_reader:
                if file == "users":
                    sql = "INSERT INTO Users (discord_id, first_name, last_name, team, active) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), row[1], row[2], int(row[3]), int(bool(row[4]))))

                elif file == "pings":
                    sql = "INSERT INTO Pings (thread_id, message_id, severity, description) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), int(row[1]), row[2], row[3],))

                elif file == "activeclaims":
                    sql = "INSERT INTO ActiveClaims (claim_message_id, case_num, tech_id, claim_time) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), row[1], int(row[2]), row[3],))

                elif file == "announcements":
                    sql = "INSERT INTO Announcements (message_id, case_message_id, title, description, user, end_time, active) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), int(row[1]), row[2], row[3], int(row[4]), row[5], int(bool(row[6])),))

                elif file == "checkedclaims":
                    sql = "INSERT INTO CheckedClaims (checker_message_id, case_num, tech_id, lead_id, claim_time, complete_time, check_time, status, ping_thread_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), row[1], int(row[2]), int(row[3]), row[4], row[5], row[6], row[7], None if len(row[8]) == 0 else int(row[8])))

                elif file == "completedclaims":
                    sql = "INSERT INTO CompletedClaims (checker_message_id, case_num, tech_id, claim_time, complete_time) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), row[1], int(row[2]), row[3], row[4],))
                elif file == "outages":
                    sql = "INSERT INTO Outages (message_id, case_message_id, service, parent_case, description, troubleshooting_steps, resolution_time, user, active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (int(row[0]), row[1], row[2], None if len(row[3]) == 0 else row[3], None if len(row[4]) == 0 else row[4], None if len(row[5]) == 0 else row[5], row[6], int(row[7]), int(bool(row[8])),))

            connection.commit()
