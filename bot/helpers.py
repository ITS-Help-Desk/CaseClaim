"""This file contains functions that are shared by commands and views
all throughout this bot.
"""

import csv
from typing import Optional, Any
import json

from bot.claim import Claim
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
        'may': '05',
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
    except:
        raise ValueError('Not a month')
    

def find_case(case_num='', message_id=-1, user_id=-1, pinged=False) -> Optional[Claim]:
    """Finds the first case in the log file that matches
    the provided information and hasn't been pinged.

    Args:
        message_id (int): The ID of the original claim message on log.

    Returns:
        Optional[Claim]: The claim representation from the log file.
    """
    with open('log.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # Test case number
            if len(case_num) != 0 and case_num != row[2]:
                continue

            # Test if message ID matches
            if message_id != -1 and row[0] != str(message_id):
                continue
            
            # Test if user ID matches
            if user_id != -1 and row[3] != str(user_id):
                continue
            
            # Test if pinged
            if (row[5] == Status.PINGED) != pinged:
                continue
            return Claim.load_from_row(row)
    
    with open('active_cases.json', 'r') as f:
        new_data: dict[str, Any] = json.load(f)
        for key in new_data.keys():
            claim_case_num = str(new_data[key]["case_num"])
            claim_user_id = int(new_data[key]["tech_id"])

            # Test case number
            if len(case_num) != 0 and case_num != claim_case_num:
                continue

            # Test if message ID matches
            if message_id != -1 and int(key) != message_id:
                continue
            
            # Test if user ID matches
            if user_id != -1 and user_id != claim_user_id:
                continue
            return Claim.load_from_json(new_data[key])
    
    # Case couldn't be found, return  None
    return None


def remove_case(user_id: int, case_num: str) -> None:
    """Removes the first case in the log file that
    matches the provided information and hasn't been pinged.

    Args:
        user_id (int): The user for the case that needs to be pinged.
        case_num (str): The case number of the case that needs to be pinged.
    """
    # Collect rows with this case
    lines = []
    found_row = False
    with open('log.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # Exclude row once found
            if not found_row and row[2] == case_num and row[5] != Status.PINGED and int(row[3]) == user_id:
                found_row = True
                continue # Don't add to the lines list
            
            lines.append(row)
                
    with open('log.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(lines)
