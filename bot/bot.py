from aiohttp import ClientSession
import asyncio
from discord.ext import commands, tasks
from mysql.connector import MySQLConnection
from typing import Any, OrderedDict

from bot.cogs.claim_command import ClaimCommand
from bot.cogs.mycases_command import MyCasesCommand
from bot.cogs.caseinfo_command import CaseInfoCommand
from bot.cogs.report_command import ReportCommand
from bot.cogs.join_command import JoinCommand
from bot.cogs.announcement_command import AnnouncementCommand
from bot.cogs.help_command import HelpCommand
from bot.cogs.leaderboard_command import LeaderboardCommand
from bot.cogs.casedist_command import CaseDistCommand
from bot.cogs.leadstats_command import LeadStatsCommand
from bot.cogs.ping_command import PingCommand
from bot.cogs.award_command import AwardCommand
from bot.cogs.evaldata_command import EvaldataCommand
from bot.cogs.heatmap_command import HeatmapCommand
from bot.cogs.geneval_command import GenEvalCommand

from bot.views.affirm_view import AffirmView
from bot.views.claim_view import ClaimView
from bot.views.check_view import CheckView
from bot.views.check_view_red import CheckViewRed
from bot.views.resolve_ping_view import ResolvePingView
from bot.views.outage_view import OutageView
from bot.views.leaderboard_view import LeaderboardView
from bot.views.leadstats_view import LeadStatsView
from bot.views.kudos_view import KudosView
from bot.views.force_complete_view import ForceCompleteView
from bot.views.force_unclaim_view import ForceUnclaimView

from bot.models.outage import Outage
from bot.models.team import Team

from bot.helpers.other import *
from bot.helpers.leaderboard_helpers import *


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    error_channel: int
    announcement_channel: int
    bot_channel: int
    connection: MySQLConnection

    def __init__(self, config: dict[str, Any], connection: MySQLConnection):
        """Initializes the bot (doesn't start it), and initializes some
        instance variables relating to file locations.
        """
        self.cases_channel = int(config["cases_channel"])
        self.claims_channel = int(config["claims_channel"])
        self.error_channel = int(config["error_channel"])
        self.announcement_channel = int(config["announcement_channel"])
        self.log_channel = int(config["log_channel"])
        self.bot_channel = int(config["bot_channel"])

        self.connection = connection

        self.embed_color = discord.Color.from_rgb(30, 31, 34)

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
        dev_role = discord.utils.get(user.guild.roles, name="Dev")
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

    @tasks.loop(seconds=86400)  # repeat once a day
    async def check_teams_loop(self):
        """Checks every user and stores their role in the Users table.
        This happens once a day to ensure that the Users table is up-to-date.
        """
        users = User.get_all(self.connection)

        cases_channel = await self.fetch_channel(self.cases_channel)

        for user in users:
            try:
                discord_user = await cases_channel.guild.fetch_member(user.discord_id)

                # Collect all roles of a user
                role_ids = []
                for role in discord_user.roles:
                    role_ids.append(role.id)

                # Go through each team and figure out what team the user is on
                for team in Team.get_all(self.connection):
                    if team.role_id == 0:
                        continue
                    if team.role_id in role_ids and team.role_id != user.team_id:
                        user.add_team(self.connection, team)
                        break

            except:
                pass  # ignore exception, usually caused by a user leaving the server

        result = LeaderboardResults(CheckedClaim.get_all_leaderboard(self.connection, datetime.datetime.now().year), TeamPoint.get_all(self.connection), datetime.datetime.now(), None)
        await self.update_icon(result.ordered_team_month)

    async def update_icon(self, team_ranks: OrderedDict):
        """Updates the server icon using the team that is in first place for the month
        on the leaderboard

        Args:
            team_ranks (OrderedDict): An ordered dictionary of all the teams and their counts
        """
        if len(list(team_ranks.keys())) == 0:
            return

        first_place = list(team_ranks.keys())[0]
        first_place_team = Team.from_role_id(self.connection, first_place)

        new_icon = first_place_team.image_url
        ch = await self.fetch_channel(self.cases_channel)

        # Use aiohttp Clientsession to asynchronously scrape the attachment url and read the data to a variable
        async with ClientSession() as session:
            async with session.get(new_icon) as response:
                # If site response, read the response data into img_data
                if response.status == 200:
                    img_data = await response.read()

        # Update the guild icon with the data stored in img_data
        await ch.guild.edit(icon=img_data)

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
        self.add_view(AffirmView(self))
        self.add_view(CheckView(self))
        self.add_view(CheckViewRed(self))
        self.add_view(ClaimView(self))
        self.add_view(ForceCompleteView(self))
        self.add_view(ForceUnclaimView(self))
        self.add_view(KudosView(self))
        self.add_view(LeaderboardView(self))
        self.add_view(LeadStatsView(self))
        self.add_view(OutageView(self))
        self.add_view(ResolvePingView(self))

    async def on_ready(self):
        """Loads all commands stored in the cogs folder and starts the bot.
        After this function is run, the bot is fully operational.
        """
        print(f'Logged in as {self.user}!')

        # Load all commands
        await self.add_cog(HelpCommand(self))
        await self.add_cog(ClaimCommand(self))
        await self.add_cog(MyCasesCommand(self))
        await self.add_cog(CaseInfoCommand(self))
        await self.add_cog(JoinCommand(self))

        await self.add_cog(ReportCommand(self))
        await self.add_cog(GenEvalCommand(self))
        await self.add_cog(EvaldataCommand(self))
        await self.add_cog(HeatmapCommand(self))

        await self.add_cog(LeaderboardCommand(self))

        await self.add_cog(CaseDistCommand(self))
        await self.add_cog(LeadStatsCommand(self))
        await self.add_cog(PingCommand(self))
        await self.add_cog(AwardCommand(self))

        await self.add_cog(AnnouncementCommand(self))

        self.check_teams_loop.start()
        self.resend_outages_loop.start()
        self.reset_connection_loop.start()
    
        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))
