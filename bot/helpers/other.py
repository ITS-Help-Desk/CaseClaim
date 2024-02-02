"""This file contains functions that are shared by commands and views
all throughout this bot.
"""
import time
from pytz import timezone

import discord
import datetime

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
    if t.month == 1 and t.day < 29:
        return "Winter"
    
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
