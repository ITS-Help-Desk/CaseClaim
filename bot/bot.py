import json
from typing import Any, Optional
from discord.ext import commands
import discord

from .cogs.mickie_command import MickieCommand
from .cogs.help_command import HelpCommand
from .cogs.report_command import ReportCommand
from .cogs.claim_command import ClaimCommand
from .cogs.ping_command import PingCommand
from .cogs.update_percent_command import UpdatePercentCommand
from .cogs.caseinfo_command import CaseInfoCommand
from .cogs.mycases_command import MyCasesCommand
from .cogs.leaderboard_command import LeaderboardCommand

from .views.lead_view import LeadView
from .views.tech_view import TechView
from .views.leaderboard_view import LeaderboardView
from .views.ping_view import PingView

from bot.claim import Claim

import traceback


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    active_cases: dict[int, Claim]

    def __init__(self, **options):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """

        # Load cases from active_cases file
        self.load_cases()

        self.review_rate = 1.0
        self.embed_color = discord.Color.from_rgb(117, 190, 233)

        # Initialize bot settings
        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')
        
        '''@self.event
        async def on_error(event, *args, **kwargs):
            message = args[0] # Gets the message object
            print("test")
            print(traceback.format_exc())

            await self.send_message(message.channel, "You caused an error!") #send the message to the channel'''


    def add_case(self, case: Claim, store=True) -> None:
        """Adds a case to the list of actively worked on cases.

        Args:
            case (Claim): The case that is being added
            store (bool): Whether or not to store on file (defaults to True).
        """
        if case.message_id == None:
            raise ValueError("Case message ID not provided!")
        
        self.active_cases[case.message_id] = case
        if store:
            self.store_cases()
    

    def get_case(self, message_id: int) -> Optional[Claim]:
        """Gets a case from the list of actively worked-on cases.

        Args:
            message_id (int): The id of the original message the bot responded with.

        Returns:
            Optional[Claim]: The claim (if it exists).
        """
        return self.active_cases.get(message_id, None)
    

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
            if case.case_num == case_num and case.status != "Complete":
                return True
        return False


    def remove_case(self, message_id: int) -> None:
        """Removes a case from the list of actively worked on cases.

        Args:
            message_id (int): The message id of the case that is being removed.
        """
        try:
            del self.active_cases[message_id]
        except KeyError:
            pass
        self.store_cases()
    

    def store_cases(self) -> None:
        """Stores the actively worked on cases into the file actives_cases.json
        """
        new_data = {}
        for message_id in self.active_cases.keys():
            c = self.get_case(message_id)
            if c is not None:
                new_data[str(message_id)] = c.json_format()
        with open('active_cases.json', 'w') as f:
            json.dump(new_data, f)
    

    def load_cases(self) -> None:
        """Loads the actively worked on cases from the file active_cases.json
        """
        self.active_cases = {}
        with open('active_cases.json', 'r') as f:
            new_data: dict[str, Any] = json.load(f)
            for message_id in new_data.keys():
                c = Claim.load_from_json(new_data[message_id])
                self.active_cases[int(message_id)] = c
    

    def check_if_lead(self, user: discord.Member) -> bool:
        """Checks if a given user is a lead or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the Lead role.
        """
        lead_role = discord.utils.get(user.guild.roles, name="Lead")
        return lead_role in user.roles


    async def setup_hook(self):
        """Sets up the views so that they can be persistently loaded
        """
        self.add_view(TechView(self))
        self.add_view(LeadView(self))

        self.add_view(LeaderboardView(self))
        self.add_view(PingView(self))
        

    async def on_ready(self):
        """Loads all commands stored in the cogs folder and starts the bot.
        After this function is run, the bot is fully operational.
        """
        print(f'Logged in as {self.user}!')

        # Load all commands
        await self.add_cog(MickieCommand(self))
        await self.add_cog(HelpCommand(self))
        await self.add_cog(ReportCommand(self))
        await self.add_cog(ClaimCommand(self))
        await self.add_cog(PingCommand(self))
        await self.add_cog(UpdatePercentCommand(self))
        await self.add_cog(CaseInfoCommand(self))
        await self.add_cog(MyCasesCommand(self))
        await self.add_cog(LeaderboardCommand(self))


        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))
