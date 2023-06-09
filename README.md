# Case Claim Bot
This repository contains the code to run the USD ITS Help Desk Case Claim bot. This bot is intended to be run with Python [3.11.3](https://www.python.org/downloads/release/python-3113/).

## How to Run
1. Verify Python version

    On Windows: `python -V` OR `py -V`
    
    On Mac: `python3 -V`

    Ensure that the result of these commands is `Python 3.11.3`.
2. Download dependencies

    On Windows:
    `python -m pip install -r requirements.txt` OR `py -m pip install -r requirements.txt`

    On Mac:
    `python3 -m pip3 install -r requirements.txt`

3. Run the `main.py` file
4. Add required information to `config.json`
5. Run the `main.py` file


## File Structure
```bash
.
├── main.py # Organizes files and runs bot
├── token.txt # Token for the Discord bot
├── config.json # Channel IDs
├── active_cases.json # All cases being worked on
├── log.csv # Information on all cases
├── temp.csv # Stores reports
└── bot
    ├── bot.py # Runs main operations for storing cases
    ├── claim.py # OOP representation of a claim
    ├── paginator.py # Creates embed pages that can be traversed
    ├── helpers.py # Lists some shared functions
    ├── cogs
        ├── claim_command.py # /claim
        ├── ping_command.py # /ping
        ├── help_command.py # /help
        ├── mycases_command.py # /mycases
        ├── leaderboard_command.py # /leaderboard
        ├── mickie_command.py # /mickie
        ├── caseinfo_command.py # /caseinfo
        ├── update_percent_command.py # /update_percent
        └── report_command.py # /report
    ├── modals
        ├── assessment_modal.py # Feedback form for techs affirming pings
        └── feedback_modal.py # Feedback form for pings
    └── views
        ├── leaderboard_view.py # Refresh and My Rank buttons
        ├── ping_view.py # Affirm and Resolve buttons
        ├── resolve_ping_view.py # Change Status and Keep Pinged buttons
        ├── lead_view.py # Check and Ping buttons
        └── tech_view.py # Complete and Unclaim buttons
```

## Commands
- /claim **<case_num>**
    - Allows a tech to claim a case and ensure that no other techs will work on that case.
    - Once a case is completed, a lead is able to review that case, and ping it if necessary.
    - When a lead pings a case, they can provide a description and a severity level.
    - This feedback will be shared with the tech in a private thread.
- /help
    - Shows all of commands for the bot with descriptions.
- /mickie
    - A fun command that essentially allows users to ping the bot and ensure it's online.
- /ping **<case_num>** **\<user>**
    - Allows a lead to manually ping a case and provide feedback to a tech.
    - Leads are able to write a description and severity level, which will be shared with the tech in a private thread.
- /report **\[user]** **\[month]** **\[pinged]**
    - Allows a lead to instantly create a report on filtered cases.
    - Leads can filter depending on a user, month, or whether or not the case was pinged.
    - These parameters are optional and can be used in conjunction with one another.
- /update_percentage **\<percentage>**
    - Allows a lead to change the percentage of cases that are sent to review.
    - Percentage defaults to 100% every restart.
- /caseinfo **\<case_num>**
    - Allows a lead or a tech to see the history of a case and see who's worked on it previously.
    - Techs can see who's worked on the case and the timestamp.
    - Leads can see the case comments in addition to who's worked on it and the timestamp.
- /mycases
    - Allows a user to see a list of cases they've worked on.
    - Shows a paginated list containing the time and case numbers.
- /leaderboard
    - Allows a user to see a leaderboard of all other users by case claim amount.
    - Shows a paginated view of each user and how many cases they've claimed.

## Dependencies
- discord.py [2.2.2](https://pypi.org/project/discord.py/) 