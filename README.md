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
    - 
## Commands (for Leads)
- /report **\[user]** **\[month]** **\[pinged]**
    - Allows a lead to instantly create a report on filtered cases.
    - Leads can filter depending on a user, month, or whether or not the case was pinged.
    - These parameters are optional and can be used in conjunction with one another.
- /announcement **<Outage/Announcement>**
  - Allows a PA/lead to make an announcement or an outage.
  - Prompts the PA/lead with a modal where they can input information
  - A message will appear in the announcements channel and a sticky message will appear in the cases channel
- /ping **<user>** **<case_num>**
  - Allows a lead to manually ping a case after it has been checked
  - Prompts a lead with a modal to input standard pinging information
- /heatmap **<year>** **\[month]**
  - Shows a heatmap of what lead are checking certain tech's claims
  - Can be used for one month or an entire year
- /evaldata **<year>** **\[month]**
  - Returns two spreadsheets with data that can be used for monthly evaluations
  - One spreadsheet is for data relating to techs, the other spreadsheet has data relating to leads
- /casedist **\<days>**
    - Allows a lead to see the distribution of case claim time throughout the day.
    - Uses matplotlib to create a histogram displaying the information.
- /award
    - Allows a lead to reward a team points that will be logged in the MySQL database.
    - Sends a message to the #bot channel informing everyone of the award and the reason why it was given.


## Dependencies
- discord.py [2.2.2](https://pypi.org/project/discord.py/)
- matplotlib [3.7.2](https://pypi.org/project/matplotlib/)
- pandas [2.1.0](https://pypi.org/project/pandas/)
- mysql-connector-python [8.1.0](https://pypi.org/project/mysql-connector-python/)
- Flask [3.0.0](https://pypi.org/project/Flask/)
- aiohttp [3.9.1](https://pypi.org/project/aiohttp/)
- pytz [2023.3](https://pypi.org/project/pytz/)
- numpy [1.26.3](https://pypi.org/project/numpy/)
- python-dotenv [1.0.1](https://pypi.org/project/python-dotenv/)
