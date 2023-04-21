from discord.ext import commands
import discord
from cogs import mickie
from cogs import help
from cogs import report
from cogs import claim
import os
import csv


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int

    def __init__(self, **options):
        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')

        self.file_path = os.path.abspath(os.getcwd())
        if '/' in self.file_path:
            self.log_file_path = f"{self.file_path}/log.csv"
        else:
            self.log_file_path = f"{self.file_path}\\log.csv"



    def log_case(self, timestamp, casenum, status, lead, tech):
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
        print(f'Logged in as {self.user}!')

        await self.add_cog(mickie.Mickie(self))
        await self.add_cog(help.Help(self))
        await self.add_cog(report.Report(self))
        await self.add_cog(claim.Claim(self))
        
        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))