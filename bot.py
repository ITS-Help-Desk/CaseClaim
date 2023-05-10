from discord.ext import commands
import discord
from cogs import mickie
from cogs import help
from cogs import report
from cogs import claim
import os
import csv
from cogs.case import Case


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    active_cases: dict[int, Case]

    def __init__(self, **options):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """
        self.active_cases = {}

        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')

        self.file_path = os.path.abspath(os.getcwd())
        if '/' in self.file_path:
            self.log_file_path = f"{self.file_path}/log.csv"
        else:
            self.log_file_path = f"{self.file_path}\\log.csv"


    def add_case(self, case: Case) -> None:
        """Adds a case to the list of actively worked on cases.

        Args:
            case (Case): The case that is being added
        """
        if case.message_id == None:
            raise ValueError("Case message ID not provided!")
        
        self.active_cases[case.message_id] = case
    
    def check_if_claimed(self, case_num: str) -> bool:
        """Checks if a case has already been claimed or not by
        looking it up in the active_cases dict.

        Args:
            case_num (str): The number of the case trying to be claimed

        Returns:
            bool: True or False if the case has been claimed or not
        """
        for message_id in list(self.active_cases.keys()):
            case = self.active_cases[message_id]
            if case.case_num == case_num:
                return True
        return False

    def remove_case(self, message_id: int) -> None:
        """Removes a case from the list of actively worked on cases.

        Args:
            case (Case): The case that is being removed.
        """
        del self.active_cases[message_id]

    
    def log_case(self, case: Case) -> None:
        """Logs the case to the logfile.

        Args:
            case (Case): The case object
        """
        
        with open(self.log_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(case.log_format())
            
        
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