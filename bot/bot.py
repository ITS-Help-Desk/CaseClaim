from discord.ext import commands, tasks
import discord
from mysql.connector import MySQLConnection
from typing import Union

from bot.cogs.claim_command import ClaimCommand
from bot.cogs.mickie_command import MickieCommand
from bot.cogs.getlog_command import GetLogCommand
from bot.cogs.mycases_command import MyCasesCommand
from bot.cogs.caseinfo_command import CaseInfoCommand
from bot.cogs.report_command import ReportCommand
from bot.cogs.join_command import JoinCommand
from bot.cogs.announcement_command import AnnouncementCommand
from bot.cogs.help_command import HelpCommand
from bot.cogs.leaderboard_command import LeaderboardCommand
from bot.cogs.case_dist import CaseDistCommand
from bot.cogs.leadstats_command import LeadStatsCommand
from bot.cogs.export_command import ExportCommand

from bot.views.claim_view import ClaimView
from bot.views.affirm_view import AffirmView
from bot.views.check_view import CheckView
from bot.views.check_view_red import CheckViewRed
from bot.views.resolve_ping_view import ResolvePingView
from bot.views.outage_view import OutageView
from bot.views.leaderboard_view import LeaderboardView
from bot.views.leadstats_view import LeadStatsView
from bot.views.kudos_view import KudosView

from bot.models.outage import Outage
from bot.models.checked_claim import CheckedClaim


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    error_channel: int
    announcement_channel: int
    connection: MySQLConnection

    def __init__(self, config: dict[str, Union[int, str]], connection: MySQLConnection):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """
        self.cases_channel = int(config["cases_channel"])
        self.claims_channel = int(config["claims_channel"])
        self.error_channel = int(config["error_channel"])
        self.announcement_channel = int(config["announcement_channel"])

        self.connection = connection

        self.embed_color = discord.Color.from_rgb(117, 190, 233)

        self.resend_outages = False

        # Initialize bot settings
        intents = discord.Intents.default()
        intents.message_content = True  
        super().__init__(intents=intents, command_prefix='/')

    @staticmethod
    def check_if_lead(user: discord.Member) -> bool:
        """Checks if a given user is a lead or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the Lead role.
        """
        lead_role = discord.utils.get(user.guild.roles, name="Lead")
        return lead_role in user.roles

    @staticmethod
    def check_if_dev(user: discord.Member) -> bool:
        """Checks if a given user is a dev or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the dev role.
        """
        dev_role = discord.utils.get(user.guild.roles, name="dev")
        return dev_role in user.roles

    @staticmethod
    def check_if_pa(user: discord.Member) -> bool:
        """Checks if a given user is a PA or not.

        Args:
            user (Union[discord.Member, discord.User]): The Discord user.

        Returns:
            bool: Whether or not they have the dev role.
        """
        dev_role = discord.utils.get(user.guild.roles, name="Phone Analyst")
        return dev_role in user.roles

    @tasks.loop(seconds=5)  # repeat after every 5 seconds
    async def resend_outages_loop(self):
        """Resends all the outages to the #cases channel.

        The self.resend_outages bool will be set to True anytime someone claims a case.
        """
        if self.resend_outages:
            await Outage.resend(self)
            self.resend_outages = False

    @tasks.loop(seconds=1800)  # repeat after every 30 minutes
    async def reset_connection_loop(self):
        """Resets the bots connection every 30 minutes.

        Occasionally the bot will disconnect because of inactivity, pinging
        the MySQL server will prevent this.
        """
        CheckedClaim.search(self.connection)

    async def setup_hook(self):
        """Sets up the views so that they can be persistently loaded
        """
        self.add_view(ClaimView(self))
        self.add_view(AffirmView(self))
        self.add_view(CheckView(self))
        self.add_view(CheckViewRed(self))
        self.add_view(ResolvePingView(self))
        self.add_view(OutageView(self))
        self.add_view(LeadStatsView(self))
        self.add_view(LeaderboardView(self))
        self.add_view(KudosView(self))

    async def on_ready(self):
        """Loads all commands stored in the cogs folder and starts the bot.
        After this function is run, the bot is fully operational.
        """
        print(f'Logged in as {self.user}!')

        # Load all commands
        await self.add_cog(HelpCommand(self))
        await self.add_cog(ClaimCommand(self))
        await self.add_cog(MickieCommand(self))
        await self.add_cog(MyCasesCommand(self))
        await self.add_cog(CaseInfoCommand(self))
        await self.add_cog(JoinCommand(self))

        await self.add_cog(GetLogCommand(self))
        await self.add_cog(ReportCommand(self))
        await self.add_cog(LeaderboardCommand(self))
        await self.add_cog(CaseDistCommand(self))
        await self.add_cog(LeadStatsCommand(self))
        await self.add_cog(ExportCommand(self))

        await self.add_cog(AnnouncementCommand(self))

        self.resend_outages_loop.start()
        self.reset_connection_loop.start()

        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))
