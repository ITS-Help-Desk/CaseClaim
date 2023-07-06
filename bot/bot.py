from discord.ext import commands
import discord

from .claim_manager import ClaimManager
from .announcement_manager import AnnouncementManager

from .cogs.mickie_command import MickieCommand
from .cogs.help_command import HelpCommand
from .cogs.report_command import ReportCommand
from .cogs.claim_command import ClaimCommand
from .cogs.ping_command import PingCommand
from .cogs.update_percent_command import UpdatePercentCommand
from .cogs.caseinfo_command import CaseInfoCommand
from .cogs.mycases_command import MyCasesCommand
from .cogs.leaderboard_command import LeaderboardCommand
from .cogs.leadstats_command import LeadStatsCommand
from .cogs.getlog_command import GetLogCommand
from .cogs.announcement_command import AnnouncementCommand

from .views.lead_view import LeadView
from .views.lead_view_red import LeadViewRed
from .views.tech_view import TechView
from .views.leaderboard_view import LeaderboardView
from .views.leadstats_view import LeadStatsView
from .views.ping_view import PingView


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    error_channel: int
    announcement_channel: int

    def __init__(self, **options):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """

        self.claim_manager = ClaimManager(self)
        self.announcement_manager = AnnouncementManager(self)

        self.review_rate = 1.0
        self.embed_color = discord.Color.from_rgb(117, 190, 233)

        # Initialize bot settings
        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')
    

    def check_if_lead(self, user: discord.Member) -> bool:
        """Checks if a given user is a lead or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the Lead role.
        """
        lead_role = discord.utils.get(user.guild.roles, name="Lead")
        return lead_role in user.roles


    def check_if_dev(self, user: discord.Member) -> bool:
        """Checks if a given user is a dev or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the dev role.
        """
        dev_role = discord.utils.get(user.guild.roles, name="dev")
        return dev_role in user.roles


    def check_if_pa(self, user: discord.Member) -> bool:
        """Checks if a given user is a PA or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the dev role.
        """
        dev_role = discord.utils.get(user.guild.roles, name="Phone Analyst")
        return dev_role in user.roles


    async def setup_hook(self):
        """Sets up the views so that they can be persistently loaded
        """
        self.add_view(TechView(self))
        self.add_view(LeadView(self))
        self.add_view(LeadViewRed(self))

        self.add_view(LeaderboardView(self))
        self.add_view(LeadStatsView(self))
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
        await self.add_cog(GetLogCommand(self))
        await self.add_cog(LeaderboardCommand(self))
        await self.add_cog(LeadStatsCommand(self))
        await self.add_cog(AnnouncementCommand(self))

        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))
