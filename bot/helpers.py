"""This file contains functions that are shared by commands and views
all throughout this bot.
"""
import time
from pytz import timezone
from collections import OrderedDict
from typing import Optional

import discord
import datetime

from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
from bot.models.team_point import TeamPoint
from bot.status import Status


def month_number_to_name(month_number: int) -> str:
    """Converts a month number to the actual name.
    (e.g. 1 -> January)

    Args:
        month_number (int): The number of the month (from 1 to 12)

    Raises:
        ValueError: If the number provided is < 1 or > 12

    Returns:
        str: The full name of the month (e.g. "February")
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    if 1 <= month_number <= 12:
        return month_names[month_number - 1]
    else:
        raise ValueError("Invalid month number")


def month_string_to_number(month_name: str) -> str:
    """Converts the name of a month to the corresponding number

    Args:
        month_name (str): The full name or abbreviation of a month.

    Raises:
        ValueError: When the provided month_name isn't valid.

    Returns:
        str: The number of the actual month (e.g. "jan" -> "01")
    """
    m = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12',
        'january': '01',
        'february': '02',
        'march': '03',
        'april': '04',
        'june': '06',
        'july': '07',
        'august': '08',
        'september': '09',
        'october': '10',
        'november': '11',
        'december': '12'
    }
    try:
        s = month_name.strip().lower()
        out = m[s]
        return out
    except Exception:
        raise ValueError('Not a month')


def create_paginator_embeds(data: list[str], title: str, embed_color: discord.Color) -> list[discord.Embed]:
    """Creates a list of embeds that can be used with a paginator.

    Args:
        data (list[str]): The list of case descriptions.
        title (str): The title for each of the embeds
        embed_color (discord.Color): The color of the embed

    Returns:
        list[discord.Embed]: A list of embeds for the paginator.
    """
    # Create a list of embeds to paginate
    embeds = []
    i = 0
    data_len = len(data)

    # Go through all cases
    while i < data_len:
        # Create an embed for every 10 cases
        new_embed = discord.Embed(title=title)
        new_embed.colour = embed_color
        description = ''

        # Add ten (or fewer) cases
        for j in range(min(10, len(data))):
            row = data.pop(0)
            description += row + '\n'

        new_embed.description = description
        embeds.append(new_embed)
        i += 10

    return embeds


def get_semester(t: datetime.datetime) -> str:
    """Returns the semester that the datetime object is located in.

    Jan - May -> Spring
    Jun - Aug 20 -> Summer
    Aug 21 - Dec -> Winter

    Args:
        t (datetime.datetime): The datetime object

    Returns:
        str - The name of the semester
    """
    if 1 <= t.month <= 5:
        return "Spring"

    if 6 <= t.month < 8:
        return "Summer"

    if t.month == 8 and t.day < 25:
        return "Summer"

    if t.month == 8 and t.day == 25 and t.hour < 15:
        return "Summer"

    return "Fall"


def is_working_time(t: datetime.datetime, holidays: list[str]) -> bool:
    """Determines whether or not a provided datetime falls within working hours.
    Can be used to time pings or other bot operations to only happen
    during working time.

    Args:
        t (datetime): The time that is being evaluated (in UTC)
        holidays (list[str]): The list of holidays ["1-1", "7-5",...]

    Returns:
        bool - Whether or not the datetime falls in working hours
    """
    date = f"{int(t.month)}-{int(t.day)}"

    t = t.astimezone(timezone("UTC"))
    now_pst = t.astimezone(timezone('America/Los_Angeles'))

    if date in holidays:
        # Holiday
        return False

    if time.localtime().tm_isdst == 1:
        # Daylight savings time
        offset = 0
    else:
        # Standard time
        offset = -1

    if 0 <= now_pst.weekday() <= 3:
        # Mon - Thur
        return 7 + offset <= now_pst.hour < 18 + offset
    elif t.weekday() == 4:
        # Friday
        return 7 + offset <= now_pst.hour < 17 + offset
    else:
        # Sat - Sun
        return False


class LeaderboardResults:
    def __init__(self, claims: list[CheckedClaim], team_points: list[TeamPoint], date: datetime.datetime, user: Optional[User]):
        """Creates a data structure for storing leaderboard data:
        counts (dict[int,int]) --> Used for storing how many cases each tech has
        ping_counts (int) --> The amount of pings a user has
        sorted_keys (list[int]) --> The keys of the counts dict in order from most to least claims
        ordered (OrderedDict) --> The ordered dictionary for the counts dict

        Args:
            claims (list[CheckedClaim]): The list of claims to be sifted through
            team_points (list[TeamPoint]): The list of all TeamPoints
            date (datetime.datetime): The date (used for monthly cases)
            user (Optional[User]): The user (used for pinged counts)
        """
        self.month_counts: dict[int, int] = {}  # General check counts for the month
        self.semester_counts: dict[int, int] = {}  # General check counts for the semester

        self.month_team_counts: dict[int, int] = {}  # General team counts for the month
        self.semester_team_counts: dict[int, int] = {}  # General team counts for the semester

        self.month_ping_count = 0  # Ping count for the user for the month
        self.semester_ping_count = 0  # Ping count for the user for the semester

        current_sem = get_semester(date)
        for claim in claims:
            # Filter out claims from different semesters
            if get_semester(claim.claim_time) != current_sem:
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

        self.month_team_sorted_keys: list[int] = sorted(self.month_team_counts, key=self.month_team_counts.get, reverse=True)
        self.semester_team_sorted_keys: list[int] = sorted(self.semester_team_counts, key=self.semester_team_counts.get, reverse=True)

        # Create ordered dictionaries
        self.ordered_month: OrderedDict = OrderedDict()
        self.ordered_semester: OrderedDict = OrderedDict()

        self.ordered_team_month: OrderedDict = OrderedDict()
        self.ordered_team_semester: OrderedDict = OrderedDict()

        for key in self.month_sorted_keys:
            self.ordered_month[key] = self.month_counts[key]

        for key in self.semester_sorted_keys:
            self.ordered_semester[key] = self.semester_counts[key]

        for key in self.month_team_sorted_keys:
            self.ordered_team_month[key] = self.month_team_counts[key]

        for key in self.semester_team_sorted_keys:
            self.ordered_team_semester[key] = self.semester_team_counts[key]

        for tp in team_points:
            if tp.timestamp.year != date.year or not get_semester(tp.timestamp) == get_semester(date):
                continue

            self.ordered_team_semester.setdefault(tp.role_id, 0)
            self.ordered_team_semester[tp.role_id] += tp.points
            if tp.timestamp.month == date.month:
                self.ordered_team_month.setdefault(tp.role_id, 0)
                self.ordered_team_month[tp.role_id] += tp.points
