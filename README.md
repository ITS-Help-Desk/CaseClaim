# Case Claim Bot
This repository contains the code to run the USD ITS Help Desk Case Claim bot. This bot is intended to be run with Python [3.11.3](https://www.python.org/downloads/release/python-3113/).

For information about how to run the bot, troubleshooting, and development guides, please refer to the [Wiki](https://github.com/ajockelle/CaseClaim/wiki).

## Commands
- /claim **<case_num>**
    - Allows a tech to claim a case and ensure that no other techs will work on that case.
    - Once a case is completed, a lead is able to review that case, and ping it if necessary.
    - When a lead pings a case, they can provide a description and a severity level.
    - This feedback will be shared with the tech in a private thread.
- /help
    - Shows all commands for the bot with descriptions.
- /join
    - Allows a user to add themselves to the `Users` table in the database.
    - Asks for a user's first and last name.
- /caseinfo **\<case_num>**
    - Allows a lead or a tech to see the history of a case and see who's worked on it previously.
    - Techs can see who's worked on the case and the timestamp.
    - Leads can see the case comments in addition to whose worked on it and the timestamp.
- /mycases
    - Allows a user to see a list of cases they've worked on.
    - Shows a paginated list containing the time and case numbers.
- /hleaderboard
  - Allows a user to see a leaderboard from any month and year.
  - Shows an ephemeral message in the same format as the normal leaderboard.
## Commands (for Leads)
- /report **\[user]** **\[month]** **\[pinged]**
    - Allows a lead to instantly create a report on filtered cases.
    - Leads can filter depending on a user, month, or whether or not the case was pinged.
    - These parameters are optional and can be used in conjunction with one another.
- /leaderboard
    - Allows a user to see a leaderboard of all other users by case claim amount.
    - Shows a paginated view of each user and how many cases they've claimed.
- /leadstats
    - Allows a user to see a leaderboard of all leads by cases they've checked and how many have been pinged
    - Uses matplotlib and pandas to create a stacked bar chart displaying the information
- /getlog
    - Allows a lead to get a copy of the log file so that they can view all messages
- /casedist **\<days>**
    - Allows a lead to see the distribution of case claim time throughout the day.
    - Uses matplotlib to create a histogram displaying the information.
- /award
    - Allows a lead to reward a team points that will be logged in the MySQL database.
    - Sends a message to the #bot channel informing everyone of the award and the reason why it was given.
## Commands (for PAs)
- /announcement **<Outage/Announcement>**
  - Allows a PA to make an announcement or an outage.
  - Prompts the PA with a modal where they can input information
  - A message will appear in the announcements channel and a sticky message will appear in the cases channel

## Dependencies
- discord.py [2.2.2](https://pypi.org/project/discord.py/)
- matplotlib [3.7.2](https://pypi.org/project/matplotlib/)
- pandas [2.1.0](https://pypi.org/project/pandas/)
- mysql-connector-python [8.1.0](https://pypi.org/project/mysql-connector-python/)
- aiohttp [3.8.3](https://pypi.org/project/aiohttp/)
- pytz [2023.3](https://pypi.org/project/pytz/)
- Flask [3.0.0](https://pypi.org/project/Flask/)
