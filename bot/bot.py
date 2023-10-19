import datetime
from collections import OrderedDict

from aiohttp import ClientSession
import asyncio
from discord.ext import commands, tasks
import discord
from mysql.connector import MySQLConnection
from typing import Any

from bot.cogs.claim_command import ClaimCommand
from bot.cogs.getlog_command import GetLogCommand
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

from bot.views.claim_view import ClaimView
from bot.views.affirm_view import AffirmView
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
from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
from bot.models.team import Team
from bot.models.pending_ping import PendingPing
from bot.models.ping import Ping
from bot.models.team_point import TeamPoint

from bot.status import Status

from bot.helpers import LeaderboardResults
from bot.helpers import is_working_time


class Bot(commands.Bot):
    cases_channel: int
    claims_channel: int
    error_channel: int
    announcement_channel: int
    bot_channel: int
    connection: MySQLConnection
    holidays: list[str]

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
        self.holidays = config["holidays"]

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
        """
        if len(list(team_ranks.keys())) == 0:
            return

        first_place = list(team_ranks.keys())[0]
        first_place_team = Team.from_role_id(self.connection, first_place)

        new_icon = first_place_team.image_url
        ch = await self.fetch_channel(self.cases_channel)

        '''use aiohttp Clientsession to asynchronously scrape the attachment url and read the data to a variable'''
        async with ClientSession() as session:
            async with session.get(new_icon) as response:
                '''if site response, read the response data into img_data'''
                if response.status == 200:
                    img_data = await response.read()

        '''update the guild icon with the data stored in img_data'''
        await ch.guild.edit(icon=img_data)

    @tasks.loop(seconds=3600)  # repeat every hour
    async def ping_loop(self):
        """Iterate through all the pending pings and send them out
        during working hours
        """
        now = datetime.datetime.now()
        pending_pings = PendingPing.get_all(self.connection)
        if is_working_time(now, self.holidays) and len(pending_pings) != 0:
            # Only send pings during working time
            case_channel = await self.fetch_channel(self.cases_channel)
            for pp in pending_pings:
                if pp.severity.lower() != "kudos":
                    await self._send_ping(pp, case_channel)
                else:
                    await self._send_kudos(pp, case_channel)

                await asyncio.sleep(5)  # prevent rate limiting

    async def _send_ping(self, pp: PendingPing, case_channel: discord.TextChannel):
        now = datetime.datetime.now()
        # Ping the case as normal
        claim = CheckedClaim.from_checker_message_id(self.connection, pp.checker_message_id)
        claim.change_status(self.connection, Status.PINGED)

        tech = await self.fetch_user(claim.tech.discord_id)
        lead = await self.fetch_user(claim.lead.discord_id)

        # During working time, send ping as normal
        fb_embed = discord.Embed(colour=discord.Color.red(), timestamp=now)

        fb_embed.description = f"<@{tech.id}>, this case has been pinged by <@{lead.id}>."

        fb_embed.add_field(name="Reason", value=str(pp.description), inline=False)

        # Add a to-do message if none is passed in
        if len(str(pp.to_do)) == 0:
            fb_embed.add_field(name="To Do",
                               value="Review and let us know if you have any questions!",
                               inline=False)
        else:
            fb_embed.add_field(name="To Do", value=str(pp.to_do), inline=False)

        fb_embed.add_field(name="", value=str("*Note: Please review this information and take actions during work hours, not after!*"))
        fb_embed.set_author(name=f"{claim.case_num}", icon_url=f'{tech.display_avatar}')
        fb_embed.set_footer(text=f"{pp.severity} severity level")

        # Create thread
        thread = await case_channel.create_thread(
            name=f"{claim.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been pinged.",
            invitable=False
        )

        # Add users to thread and send message
        await thread.add_user(tech)
        await thread.add_user(lead)
        message = await thread.send(embed=fb_embed, view=AffirmView(self))

        # Create ping object
        ping = Ping(thread.id, message.id, str(pp.severity), str(pp.description))
        ping.add_to_database(self.connection)
        claim.add_ping_thread(self.connection, thread.id)

        # Remove pending ping
        pp.remove_from_database(self.connection)

    async def _send_kudos(self, pp: PendingPing, case_channel: discord.TextChannel):
        now = datetime.datetime.now()
        claim = CheckedClaim.from_checker_message_id(self.connection, pp.checker_message_id)
        tech = await self.fetch_user(claim.tech.discord_id)

        fb_embed = discord.Embed(
            description=f"<@{tech.id}>, this case has been complimented by <@{tech.id}>.",
            colour=discord.Color.green(),
            timestamp=now
        )

        fb_embed.add_field(name="Description", value=str(pp.description), inline=False)

        fb_embed.set_author(name=f"{claim.case_num}", icon_url=f'{tech.display_avatar}')

        # Create thread
        thread = await case_channel.create_thread(
            name=f"{claim.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been complimented 😁",
            invitable=False
        )

        # Add user to thread and send message
        await thread.add_user(tech)
        message = await thread.send(embed=fb_embed, view=KudosView(self))

        # Add a Ping class to store the kudos comment data
        kudo = Ping(thread.id, message.id, "Kudos", str(pp.description))
        kudo.add_to_database(self.connection)

        claim.add_ping_thread(self.connection, kudo.thread_id)

        # Remove PendingPing
        pp.remove_from_database(self.connection)


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

        await self.add_cog(GetLogCommand(self))
        await self.add_cog(ReportCommand(self))
        await self.add_cog(LeaderboardCommand(self))
        await self.add_cog(CaseDistCommand(self))
        await self.add_cog(LeadStatsCommand(self))
        await self.add_cog(PingCommand(self))
        await self.add_cog(AwardCommand(self))

        await self.add_cog(AnnouncementCommand(self))

        self.check_teams_loop.start()
        self.resend_outages_loop.start()
        self.reset_connection_loop.start()
        self.ping_loop.start()

        synced = await self.tree.sync()
        print("{} commands synced".format(len(synced)))
