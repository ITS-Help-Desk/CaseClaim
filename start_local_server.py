from web import gui
import os

def main():
    # Export discord token to environment variable. If we go to docker remove this and do it in docker.

    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as f:
            token = f.readline().strip()
        if token:
            os.environ["DISCORD_TOKEN"] = token

    gui.load_token()
    gui.app.run()


if __name__ == "__main__":
    main()
