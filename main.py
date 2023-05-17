from bot import Bot
import json


def main():
    """Reads the bot's token from token.txt, reads the config
    info from config.json, and starts the bot according to
    these values.

    Raises:
        ValueError: when config.json doesn't exist
    """
    # Create token.txt if it doesn't already exist
    try:
        f = open('token.txt', 'x')
        f.close()
        print('Created token.txt')
    except FileExistsError:
        pass

    # Read token, if not found, take user input
    with open('token.txt', 'r') as f:
        token = f.readline().strip()
    
    if not token:
        token = input("Paste token here: ")
        with open('token.txt', 'w') as f:
            f.write(token)
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
            data = {"cases_channel": 0, "claims_channel": 0}
            json.dump(f, data)
            raise ValueError("Please add the required config information into config.csv")
    except FileExistsError:
        pass

    # Read the values from config.json
    with open('config.json', 'r') as f:
        config_data = json.load(f)
        cases_channel = config_data["cases_channel"]
        claims_channel = config_data["claims_channel"]

    
    # Create bot and run
    bot = Bot()
    bot.cases_channel = cases_channel
    bot.claims_channel = claims_channel
    bot.run(token)


if __name__ == "__main__":
    main()