import io
import datetime
from collections import OrderedDict
from typing import Optional

import pandas
from matplotlib import pyplot as plt

from bot.models.checked_claim import CheckedClaim
from bot.models.team_point import TeamPoint
from bot.models.user import User

from bot.helpers.other import *
from bot.status import Status


class LeaderboardResults:
    def __init__(self, claims: list[CheckedClaim], team_points: list[TeamPoint], date: datetime.datetime, user: Optional[User], historic=False):
        """Creates a data structure for storing leaderboard data:
        counts (dict[int,int]) --> Used for storing how many cases each tech has
        ping_counts (int) --> The amount of pings a user has
        sorted_keys (list[int]) --> The keys of the counts dict in order from most to least claims
        ordered (OrderedDict) --> The ordered dictionary for the counts dict
        historic (bool) --> Determines whether or not to count the entire semester (default: false)

        Args:
            claims (list[CheckedClaim]): The list of claims to be sifted through
            team_points (list[TeamPoint]): The list of all TeamPoints
            date (datetime.datetime): The date (used for monthly cases)
            user (Optional[User]): The user (used for pinged counts)
        """
        self.date = date

        self.month_counts: dict[int, int] = {}  # General check counts for the month
        self.semester_counts: dict[int, int] = {}  # General check counts for the semester

        self.month_team_counts: dict[int, int] = {}  # General team counts for the month
        self.semester_team_counts: dict[int, int] = {}  # General team counts for the semester

        self.month_ping_count = 0  # Ping count for the user for the month
        self.semester_ping_count = 0  # Ping count for the user for the semester

        current_sem = get_semester(date)
        for claim in claims:
            # Filter out claims from different semesters (and resolve any issues with August)
            if get_semester(claim.claim_time) != current_sem and not (claim.claim_time.month == 8 and claim.claim_time.month == date.month):
                continue

            if historic and (date.month < claim.claim_time.month or date.year != claim.claim_time.year):
                continue
            # Add semester claims
            self.semester_counts.setdefault(claim.tech.discord_id, 0)
            self.semester_counts[claim.tech.discord_id] += 1

            # Add to ping count (if the case was pinged)
            if user is not None and user.discord_id == claim.tech.discord_id and (claim.status == Status.PINGED or claim.status == Status.RESOLVED):
                self.semester_ping_count += 1

            # User doesn't have a team
            if claim.tech.team_id is not None and claim.tech.team_id != 0:
                # Add team claims
                self.semester_team_counts.setdefault(claim.tech.team_id, 0)
                self.semester_team_counts[claim.tech.team_id] += 1

            # Filter out cases from different months
            if claim.claim_time.month != date.month:
                continue

            # Add month claims
            self.month_counts.setdefault(claim.tech.discord_id, 0)
            self.month_counts[claim.tech.discord_id] += 1

            # User doesn't have a team
            if claim.tech.team_id is not None and claim.tech.team_id != 0:
                # Add team claims
                self.month_team_counts.setdefault(claim.tech.team_id, 0)
                self.month_team_counts[claim.tech.team_id] += 1

            # Add to ping count (if the case was pinged)
            if user is not None and user.discord_id == claim.tech.discord_id and (claim.status == Status.PINGED or claim.status == Status.RESOLVED):
                self.month_ping_count += 1

        # Sort the data
        self.month_sorted_keys: list[int] = sorted(self.month_counts, key=self.month_counts.get, reverse=True)
        self.semester_sorted_keys: list[int] = sorted(self.semester_counts, key=self.semester_counts.get, reverse=True)

        # Create ordered dictionaries
        self.ordered_month: OrderedDict = OrderedDict()
        self.ordered_semester: OrderedDict = OrderedDict()

        # Add data to ordered dictionaries
        for key in self.month_sorted_keys:
            self.ordered_month[key] = self.month_counts[key]

        for key in self.semester_sorted_keys:
            self.ordered_semester[key] = self.semester_counts[key]

        # Add extra team points
        for tp in team_points:
            if tp.timestamp.year != date.year or not get_semester(tp.timestamp) == current_sem:
                continue

            self.semester_team_counts.setdefault(tp.role_id, 0)
            self.semester_team_counts[tp.role_id] += tp.points
            if tp.timestamp.month == date.month:
                self.month_team_counts.setdefault(tp.role_id, 0)
                self.month_team_counts[tp.role_id] += tp.points

        # Sort the updated team point counts
        self.month_team_sorted_keys: list[int] = sorted(self.month_team_counts, key=self.month_team_counts.get, reverse=True)
        self.semester_team_sorted_keys: list[int] = sorted(self.semester_team_counts, key=self.semester_team_counts.get, reverse=True)

        # Create ordered dictionaries
        self.ordered_team_month: OrderedDict = OrderedDict()
        self.ordered_team_semester: OrderedDict = OrderedDict()

        # Add extra team points
        for key in self.month_team_sorted_keys:
            self.ordered_team_month[key] = self.month_team_counts[key]

        for key in self.semester_team_sorted_keys:
            self.ordered_team_semester[key] = self.semester_team_counts[key]

    def create_embed(self, bot: 'Bot', interaction: discord.Interaction) -> discord.Embed:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): A reference to the bot class
            interaction (discord.Interaction): The interaction requesting the leaderboard.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        month_ranking = ""
        # Create month written ranking
        for i in range(min(4, len(self.ordered_month.keys()))):
            user_id = list(self.ordered_month.keys())[i]
            month_ranking += f"**{i + 1}.** <@!{user_id}> | {self.ordered_month[user_id]}\n"

        semester_ranking = ""
        # Create semester written ranking
        for i in range(min(4, len(self.ordered_semester.keys()))):
            user_id = list(self.ordered_semester.keys())[i]
            semester_ranking += f"**{i + 1}.** <@!{user_id}> | {self.ordered_semester[user_id]}\n"

        month_team_ranking = ""
        # Create team written ranking
        for i in range(min(4, len(self.ordered_team_month.keys()))):
            team_id = list(self.ordered_team_month.keys())[i]
            month_team_ranking += f"**{i + 1}.** <@&{team_id}> | {self.ordered_team_month[team_id]}\n"

        semester_team_ranking = ""
        # Create team written ranking
        for i in range(min(4, len(self.ordered_team_semester.keys()))):
            team_id = list(self.ordered_team_semester.keys())[i]
            semester_team_ranking += f"**{i + 1}.** <@&{team_id}> | {self.ordered_team_semester[team_id]}\n"

        # Create embed
        embed = discord.Embed()
        embed.colour = bot.embed_color

        # Add leaderboard fields
        embed.add_field(name=f"{month_number_to_name(self.date.month)}", value="", inline=False)
        embed.add_field(name="", value=month_team_ranking, inline=True)
        embed.add_field(name="", value=month_ranking, inline=True)

        embed.add_field(name="Semester", value="", inline=False)

        embed.add_field(name="", value=semester_team_ranking, inline=True)
        embed.add_field(name="", value=semester_ranking, inline=True)

        embed.set_author(name="Leaderboard", icon_url=interaction.guild.icon.url)
        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed


class LeadstatsResults:
    def __init__(self, claims: list[CheckedClaim], date: datetime.datetime):
        self.month_counts = {}
        self.semester_counts = {}

        self.month_ping_counts = {}
        self.semester_ping_counts = {}

        self.month_kudos_counts = {}
        self.semester_kudos_counts = {}

        self.month_done_counts = {}
        self.semester_done_counts = {}

        self.total_month = {}
        self.total_semester = {}

        interaction_semester = get_semester(date)

        for claim in claims:
            # Ignore cases claimed after the provided date
            if date.month < claim.claim_time.month:
                continue

            # Initialize information as zero
            self.month_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_counts.setdefault(claim.lead.discord_id, 0)

            self.month_ping_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_ping_counts.setdefault(claim.lead.discord_id, 0)

            self.month_kudos_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_kudos_counts.setdefault(claim.lead.discord_id, 0)

            self.month_done_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_done_counts.setdefault(claim.lead.discord_id, 0)

            self.total_month.setdefault(claim.lead.discord_id, 0)
            self.total_semester.setdefault(claim.lead.discord_id, 0)

            # Organize data for month
            if claim.claim_time.year == date.year and claim.claim_time.month == date.month:
                self.total_month[claim.lead.discord_id] += 1
                if claim.status == Status.CHECKED:
                    # Add checked/done
                    self.month_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.DONE:
                    # Add done
                    self.month_done_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    # Add pinged/resolved
                    self.month_ping_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.KUDOS:
                    # Add kudos
                    self.month_kudos_counts[claim.lead.discord_id] += 1

            # Organize data for semester
            if get_semester(claim.claim_time) == interaction_semester:
                self.total_semester[claim.lead.discord_id] += 1
                if claim.status == Status.CHECKED:
                    # Add checked
                    self.semester_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.DONE:
                    # Add done
                    self.month_done_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    # Add pinged/resolved
                    self.semester_ping_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.KUDOS:
                    # Add kudos
                    self.semester_kudos_counts[claim.lead.discord_id] += 1

        self.semester_counts_sorted_keys = sorted(self.total_semester, key=self.total_semester.get, reverse=True)
        self.month_counts_sorted_keys = sorted(self.total_month, key=self.total_month.get, reverse=True)

    def convert_to_plot(self, bot: 'Bot', month: bool, title: str) -> io.BytesIO:
        """Converts data into a plot that can be sent in a Discord message. It uses three
        parallel lists in order to generate the plot using matplotlib

        Args:
            bot (Bot): An instance of the Bot class.
            month (bool): Whether or not the data should be just for the month of the whole semester
            title (str): The title of the chart

        Returns:
            io.BytesIO: The bytes that can be used to generate the graph
        """
        # Get month or semester data
        if month:
            counts = self.month_counts
            pings = self.month_ping_counts
            kudos = self.month_kudos_counts
            done = self.month_done_counts
            keys = self.month_counts_sorted_keys
        else:
            counts = self.semester_counts
            pings = self.semester_ping_counts
            kudos = self.semester_kudos_counts
            done = self.semester_done_counts
            keys = self.semester_counts_sorted_keys

        labels = []
        y0 = []
        y1 = []
        y2 = []
        y3 = []

        # Create labels and datapoints from the raw data
        for key in keys:
            total = counts[key] + done[key] + pings[key] + kudos[key]
            if total == 0:
                continue

            y0.append(done[key])
            y1.append(counts[key])
            y2.append(pings[key])
            y3.append(kudos[key])

            user = User.from_id(bot.connection, key)
            labels.append(f"{user.abb_name}\nP-{int((pings[key] / total) * 100)}%-K-{int((kudos[key] / total) * 100)}%")

        # If there's no data, create fake data to display the "No data" message
        # pandas cannot create a plot without data
        if len(y0) + len(y1) + len(y2) + len(y3) == 0:
            y0 = [0]
            y1 = [1]
            y2 = [0]
            y3 = [0]
            labels = ["No data"]

        data_stream = io.BytesIO()
        users = []

        # Create a dictionary to track the total amount of cases
        # by the number of checked cases (in order to add labels to each bar)
        labels_dict = {}

        # Each user has to be added as a list of 4 values (done, checks, pings, kudos)
        for i in range(len(y1)):
            user = []
            try:
                user.append(y1[i])
                labels_dict[y1[i]] = y0[i] + y1[i] + y2[i] + y3[i]
            except:
                pass
            try:
                user.append(y0[i])
            except:
                pass
            try:
                user.append(y2[i])
            except:
                pass
            try:
                user.append(y3[i])
            except:
                pass

            users.append(user)

        df = pandas.DataFrame(users, index=labels)
        ax = df.plot.bar(stacked=True, title=title, legend=False)
        #ax.legend(["Checks", "Pings", "Kudos"])
        plt.xticks(rotation=45, ha="right")

        # Add labels to each bar with the numeric values
        i = 0
        for c in ax.containers:
            labels = []
            for v in c:
                if v.get_height() > 20 and v.get_height() in list(labels_dict.keys()):
                    labels.append(labels_dict[v.get_height()])
                else:
                    labels.append("")
                i += 1

            # remove the labels parameter if it's not needed for customized labels
            ax.bar_label(c, labels=labels, label_type='center')

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=400)
        plt.close()
        data_stream.seek(0)

        return data_stream

    def create_embed(self, bot: 'Bot', interaction: discord.Interaction, month=True) -> tuple[discord.Embed, discord.File]:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): An instance of the Bot class.
            interaction (discord.Interaction): The interaction that generated this request
            month (bool): Whether or not the data will be sampled for the month or whole semester
        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        data_stream = self.convert_to_plot(bot, month, f"ITS Lead CC Statistics ({f'{month_number_to_name(interaction.created_at.month)}' if month else 'Semester'})")
        chart = discord.File(data_stream, filename="chart.png")

        embed = discord.Embed(title="ITS Case Check Leaderboard")
        embed.colour = bot.embed_color

        embed.set_image(url="attachment://chart.png")

        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed, chart
