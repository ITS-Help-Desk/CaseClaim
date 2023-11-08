#!./.venv/bin/python3

import os
import json
import mysql.connector
from mysql.connector import Error

from web import gui

class ConfigMissingError(Exception): pass

def main():
    # Export discord token to environment variable. If we go to docker remove this and do it in docker.

    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as f:
            token = f.readline().strip()
        if token:
            os.environ["DISCORD_TOKEN"] = token

    try:
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
    except Exception:
        raise ConfigMissingError("Config file is missing. Please run bot in cli mode and ensure config file is setup correctly")
    
    db_config = {
        'user': config_data["db_user"],
        'password': config_data["db_password"],
        'host': config_data["db_host"],
        'database': config_data["db_name"],
        'raise_on_warnings': True
    }
    
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("MySQL Database [Gui] connection successful")
    except Error as err:
        print(f"Error: '{err}'")
        quit(1)
    
    gui.load_db_connector(connection)
    gui.load_token()
    gui.app.run()


if __name__ == "__main__":
    main()
