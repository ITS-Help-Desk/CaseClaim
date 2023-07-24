"""This file contains functions that are shared by commands and views
all throughout this bot.
"""


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
