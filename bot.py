from discord.ext import commands
import discord
from cogs import mickie
from cogs import help
from cogs import report
from cogs import claim
import os
import csv
import datetime


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int

    def __init__(self, **options):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """
        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')

        self.file_path = os.path.abspath(os.getcwd())
        if '/' in self.file_path:
            self.log_file_path = f"{self.file_path}/log.csv"
        else:
            self.log_file_path = f"{self.file_path}\\log.csv"



    def log_case(self, timestamp: datetime.datetime, casenum: int, status: str, lead: str, tech: str):
        """Logs the case to the logfile.

        Args:
            timestamp (datetime.datetime): Time of the case being logged
            casenum (int): The case number in Salesforce (e.g. 00960979)
            status (str): The status of the case (any comments written by ITS leads)
            lead (str): The username of the lead who reviewed the case
            tech (str): The username of the tech who handled the case
        """
        time_string = str(timestamp)
        date_and_time = time_string.split(" ")
        truncated_time = date_and_time[1][:5]
        info = [[date_and_time[0], truncated_time, casenum, tech, status, lead]]
        with open(self.log_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for element in info:
                writer.writerow(element)
        return
            
        
    async def on_ready(self):
        """Loads all commands/events stored in the cogs folder and starts the bot.
        After this function is run, the bot is fully operational.
        """
        print(f'Logged in as {self.user}!')

        # Load all commands
        await self.add_cog(mickie.Mickie(self))
        await self.add_cog(help.Help(self))
        await self.add_cog(report.Report(self))
        await self.add_cog(claim.Claim(self))
        
        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))