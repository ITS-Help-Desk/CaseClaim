from bot.bot import Bot
import json
import logging


def main():
    """Reads the bot's token from token.txt, reads the config
    info from config.json, and starts the bot according to
    these values.

    Raises:
        ValueError: when config.json doesn't exist or doesn't contain any information.
    """
    # Create token.txt if it doesn't already exist
    try:
        f = open('token.txt', 'x')
        f.close()
        print('Created token.txt')
    except FileExistsError:
        pass

    # Read token, if not found take user input
    with open('token.txt', 'r') as f:
        token = f.readline().strip()
    
    if not token:
        token = input("Paste token here: ")
        with open('token.txt', 'w') as f:
            f.write(token.strip())
            f.close()
    
    # Create log.csv if it doesn't already exist
    try:
        f = open("log.csv", "x")
        f.close()
        print('Created log.csv')
    except FileExistsError:
        pass

    # Create config.json if it doesn't already exist
    try:
        f = open("config.json", "x")
        f.close()
        print('Created config.json')

        with open("config.json", "w") as f:
            data = {"cases_channel": 0, "claims_channel": 0, "error_channel": 0}
            json.dump(data, f)
            raise ValueError("Please add the required config information into config.csv")
    except FileExistsError:
        pass

    # Create active_cases.json if it doesn't already exist
    try:
        f = open("active_cases.json", "x")
        f.close()
        print('Created active_cases.json')

        with open("active_cases.json", "w") as f:
            data = {}
            json.dump(data, f)
    except FileExistsError:
        pass

    # Read the values from config.json
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            cases_channel = config_data["cases_channel"]
            claims_channel = config_data["claims_channel"]
            error_channel = config_data["error_channel"]
            
            if cases_channel == 0 or claims_channel == 0 or error_channel == 0:
                raise ValueError()
    except:
        raise ValueError("Please add the required config information into config.csv")


    # Create bot and run
    bot = Bot()  
    bot.cases_channel = cases_channel
    bot.claims_channel = claims_channel
    bot.error_channel = error_channel

    logging.basicConfig(filename='discord.log', filemode='w', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    bot.run(token)


if __name__ == "__main__":
    main()