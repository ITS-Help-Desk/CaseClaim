# Case Claim Bot
This repository contains the code to run the USD ITS Help Desk Case Claim bot. This bot is intended to be run with Python [3.11.3](https://www.python.org/downloads/release/python-3113/).

## How to Run
1. Verify python version

    On Windows: `python -V`
    
    On Mac: `python3 -V`

    Ensure that the result of these commands is `Python 3.11.3`.
2. Download dependencies

    On Windows:
    `python -m pip3 install -r requirements.txt`

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
    ├── cogs
        ├── claim_command.py  # /claim
        ├── flag_command.py   # /flag
        ├── help_command.py   # /help
        ├── mickie_command.py # /mickie
        └── report_command.py # /report
    ├── modals
        └── feedback_modal.py # Feedback form for flagging
    └── views
        ├── lead_view.py # Check and flag buttons
        └── tech_view.py # Complete and unclaim buttons
```

## Commands
- /claim **<case_num>**
    - Allows a tech to claim a case and ensure that no other techs will work on that case.
    - Once a case is completed, a lead is able to review that case, and flag it if necessary.
    - When a lead flags a case, they can provide a description and a severity level.
    - This feedback will be shared with the tech in a private thread.
- /help
    - Shows all of commands for the bot with descriptions.
- /mickie
    - A fun command that essentially allows users to ping the bot and ensure it's online.
- /flag **<case_num>** **\<user>**
    - Allows a lead to manually flag a case and provide feedback to a tech.
    - Leads are able to write a description and severity level, which will be shared with the tech in a private thread.
- /report **\[user]** **\[month]** **\[flagged]**
    - Allows a lead to instantly create a report on filtered cases.
    - Leads can filter depending on a user, month, or whether or not the case was flagged.
    - These parameters are optional and can be used in conjunction with one another.



## TODO
### Commands to Add
- Add /leaderboard command
- Add /unflag command
- Add /caseinfo command
- Add /mycases command
- Add /quest command


### Dependencies
- discord.py [2.2.2](https://pypi.org/project/discord.py/) 