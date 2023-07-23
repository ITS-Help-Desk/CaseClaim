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
├── announcements.json # All active announcements
├── log.csv # Information on all cases
├── temp.csv # Stores reports
├── discord.log # Stores all log messages
└── bot
    ├── announcement.py # OOP representation of an announcement
    ├── announcement_manager.py # Runs main operations for storing announcements
    ├── bot.py # Initializes all commands and views
    ├── claim.py # OOP representation of a claim
    ├── claim_manager.py # Runs main operations for storing claims
    ├── helpers.py # Lists some shared functions
    ├── paginator.py # Creates embed pages that can be traversed
    ├── status.py # Lists case status enum values
    ├── cogs
        ├── announcement_command.py # /announcement
        ├── caseinfo_command.py # /caseinfo
        ├── claim_command.py # /claim
        ├── getlog_command.py # /getlog
        ├── help_command.py # /help
        ├── leaderboard_command.py # /leaderboard
        ├── leaderstats_command.py # /leadstats
        ├── mickie_command.py # /mickie
        ├── mycases_command.py # /mycases
        ├── ping_command.py # /ping        
        ├── report_command.py # /report
        └── update_percent_command.py # /update_percent
    ├── forms
        ├── announcement_modal.py # Feedback form for announcements
        ├── assessment_modal.py # Feedback form for techs affirming pings
        ├── edit_announcement_modal.py # Feedback form for editing announcements
        ├── edit_outage_modal.py # Feedback form for editing outages
        ├── feedback_modal.py # Feedback form for pings
        └── outage_modal.py # Feedback form for outages
    └── views
        ├── announcement_view.py # Update and Close buttons
        ├── lead_view.py # Check and Ping buttons
        ├── lead_view_red.py # Check and Ping buttons grayed out
        ├── leaderboard_view.py # Refresh and My Rank buttons
        ├── leadstats_view.py # Month and Semester buttons
        ├── outage_view.py # Update and Close buttons
        ├── ping_view.py # Affirm and Resolve buttons
        ├── resolve_ping_view.py # Change Status and Keep Pinged buttons
        └── tech_view.py # Complete and Unclaim buttons
```

## Config File Structure
Here's how the `config.json` file should be formatted (replace zeros with ID numbers).
```json
{
  "cases_channel": 0,
  "claims_channel": 0,
  "error_channel": 0,
  "announcement_channel": 0,
  
  "db_user": "",
  "db_password": "",
  "db_host": "",
  "db_name": ""
}
```

## Role Permissions
- Tech: `N/A`
- Lead: `Mute Members`
- Phone Analyst: `Administrator`

## Commands
- /claim **<case_num>**
    - Allows a tech to claim a case and ensure that no other techs will work on that case.
    - Once a case is completed, a lead is able to review that case, and ping it if necessary.
    - When a lead pings a case, they can provide a description and a severity level.
    - This feedback will be shared with the tech in a private thread.
- /help
    - Shows all commands for the bot with descriptions.
- /caseinfo **\<case_num>**
    - Allows a lead or a tech to see the history of a case and see who's worked on it previously.
    - Techs can see who's worked on the case and the timestamp.
    - Leads can see the case comments in addition to who's worked on it and the timestamp.
- /mycases
    - Allows a user to see a list of cases they've worked on.
    - Shows a paginated list containing the time and case numbers.
- /mickie
    - A fun command that essentially allows users to ping the bot and ensure it's online.
## Commands (for Leads)
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
- /leaderboard
    - Allows a user to see a leaderboard of all other users by case claim amount.
    - Shows a paginated view of each user and how many cases they've claimed.
- /leadstats
    - Allows a user to see a leaderboard of all leads by cases they've checked and how many have been pinged
    - Uses matplotlib to create a stacked bar chart displaying the information
- /getlog
    - Allows a lead to get a copy of the log file so that they can view all messages
- /casedist **\<days>**
    - Allows a lead to see the distribution of case claim time throughout the day.
    - Uses matplotlib to create a histogram displaying the information.
## Commands (for PAs)
- /announcement **<Outage/Announcement>**
  - Allows a PA to make an announcement or an outage.
  - Prompts the PA with a modal where they can input information
  - A message will appear in the announcements channel and a sticky message will appear in the cases channel


## Case Claim Flow Chart
![Flowchart](flowchart.png)

## Dependencies
- discord.py [2.2.2](https://pypi.org/project/discord.py/)
- matplotlib [3.7.2](https://pypi.org/project/matplotlib/)