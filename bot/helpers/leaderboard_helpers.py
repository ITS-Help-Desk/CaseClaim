import io
import datetime
from typing import Optional

from mysql.connector import MySQLConnection

from bot.models.checked_claim import CheckedClaim
from bot.models.team_point import TeamPoint
from bot.models.user import User

from bot.helpers.other import *


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


class LeadstatsResults:
    def __init__(self, claims: list[CheckedClaim], date: datetime.datetime):
        self.month_counts = {}
        self.semester_counts = {}

        self.month_ping_counts = {}
        self.semester_ping_counts = {}

        self.month_kudos_counts = {}
        self.semester_kudos_counts = {}

        interaction_semester = get_semester(date)

        for claim in claims:
            # Initialize information as zero
            self.month_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_counts.setdefault(claim.lead.discord_id, 0)

            self.month_ping_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_ping_counts.setdefault(claim.lead.discord_id, 0)

            self.month_kudos_counts.setdefault(claim.lead.discord_id, 0)
            self.semester_kudos_counts.setdefault(claim.lead.discord_id, 0)

            # Organize data for month
            if claim.claim_time.year == date.year and claim.claim_time.month == date.month:
                if claim.status == Status.CHECKED or claim.status == Status.DONE:
                    # Add checked/done
                    self.month_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    # Add pinged/resolved
                    self.month_ping_counts[claim.lead.discord_id] += 1

                elif claim.status == Status.KUDOS:
                    # Add kudos
                    self.month_kudos_counts[claim.lead.discord_id] += 1

            # Organize data for semester
            if get_semester(claim.claim_time) == interaction_semester:
                if claim.status == Status.CHECKED or claim.status == Status.DONE:
                    # Add checked/done
                    self.semester_counts[claim.lead.discord_id] += 1

                if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    # Add pinged/resolved
                    self.semester_ping_counts[claim.lead.discord_id] += 1

                if claim.status == Status.KUDOS:
                    # Add kudos
                    self.semester_kudos_counts[claim.lead.discord_id] += 1

        self.semester_counts_sorted_keys = sorted(self.semester_counts, key=self.semester_counts.get, reverse=True)
        self.month_counts_sorted_keys = sorted(self.month_counts, key=self.month_counts.get, reverse=True)

    def convert_to_plot(self, connection: MySQLConnection, month: bool, title: str) -> io.BytesIO:
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
            keys = self.month_counts_sorted_keys
        else:
            counts = self.semester_counts
            pings = self.semester_ping_counts
            kudos = self.semester_kudos_counts
            keys = self.semester_counts_sorted_keys

        labels = []
        y1 = []
        y2 = []
        y3 = []

        # Create labels and datapoints from the raw data
        for key in keys:
            total = counts[key] + pings[key] + kudos[key]
            if total == 0:
                continue

            y1.append(counts[key])
            y2.append(pings[key])
            y3.append(kudos[key])

            user = User.from_id(connection, key)
            labels.append(f"{user.abb_name}\nP-{int((pings[key] / total) * 100)}%-K-{int((kudos[key] / total) * 100)}%")

        # If there's no data, create fake data to display the "No data" message
        # pandas cannot create a plot without data
        if len(y1) + len(y2) + len(y3) == 0:
            y1 = [1]
            y2 = [0]
            y3 = [0]
            labels = ["No data"]

        data_stream = io.BytesIO()
        users = []

        # Each user has to be added as a list of 3 values (checks, pings, kudos)
        for i in range(len(y1)):
            user = []
            try:
                user.append(y1[i])
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
        
        # Change matlib pyplot backend to prevent gui's from being spawned. It is causing issues with the flask webserver/
        # See https://github.com/matplotlib/matplotlib/issues/14304/
        plt.switch_backend('Agg')

        df = pandas.DataFrame(users, index=labels)
        ax = df.plot.bar(stacked=True, title=title, legend=False)
        #ax.legend(["Checks", "Pings", "Kudos"])
        plt.xticks(rotation=45, ha="right")

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=400)
        plt.close()
        data_stream.seek(0)

        return data_stream
