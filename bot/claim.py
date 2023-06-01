import datetime
import csv
from typing import Any


class InvalidClaimError(Exception):
    pass

class Claim:
    def __init__(self, case_num: str, tech_id: int = -1, message_id: int = -1, status: str = "", lead_id: int = -1, severity_level: str = "", comments: str = ""):
        """Creates a Claim class to store all information about a claim

        Args:
            case_num (str): The case number in Salesforce (e.g. "00960979")_
            tech_id (int, optional): The Discord id of the tech who claimed the case. Defaults to -1.
            message_id (int, optional): The Discord id of the case claim message. Defaults to -1.
            status (str, optional): The status of the case ("Completed"/"Checked"/"Pinged"). Defaults to "".
            lead_id (int, optional): The Discord id of the lead who reviewed the case. Defaults to -1.
            severity_level (str, optional): The severity of the ping (if pinged). Defaults to "".
            comments (str, optional): The comments of the ping (if pinged). Defaults to "".

        Raises:
            InvalidClaimError: The case number provided isn't valid (e.i. isn't 8 digits or contains a letter).
        """
        try:
            # Test if case_num is an 8 digit number
            if case_num == None or not case_num.isdigit() or len(case_num) != 8:
                raise ValueError()
            self.case_num = case_num
        except ValueError:
            raise InvalidClaimError("Invalid case number provided!")
        
        self.tech_id = tech_id

        # Define the rest of the instance vars with (potentially) placeholder values
        self.message_id = message_id
        self.status = status
        self.lead_id = lead_id
        self.severity_level = severity_level
        self.comments = comments

    @classmethod
    def load_from_json(cls, json_file: dict[str, Any]) -> 'Claim':
        """Creates a Claim instance from data stores in a JSON file.

        Args:
            json_file (dict[str, Any]): The loaded JSON file.

        Returns:
            Claim: An instance of the Claim class preloaded with this information.
        """
        return Claim(
            case_num=json_file["case_num"],
            tech_id=int(json_file["tech_id"]),
            message_id=int(json_file["message_id"]),
            status=json_file["status"],
            lead_id=int(json_file["lead_id"]),
            severity_level=json_file["severity_level"],
            comments=json_file["comments"]
        )
        

    def log(self) -> None:
        """Logs the claim to the logfile."""
        with open('log.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.log_format())


    def log_format(self) -> list[str]:
        """Returns all of the information about the claim in the format needed to log the claim in log.csv

        Returns:
            list[str | int]: Returns a list in the format of message_id, timestamp, case_num, tech_user_ID, lead_user_ID, status, severity_level, comments
        """
        return [
            str(self.message_id),
            str(datetime.datetime.now()),
            self.case_num,
            str(self.tech_id),
            str(self.lead_id),
            self.status,
            self.severity_level,
            self.comments
        ]
    
    def json_format(self) -> dict[str, Any]:
        """Converts the claim information into a JSON format that can easily be stored.

        Returns:
            dict[str, Any]: The dictionary that can immediately be stored in a JSON file.
        """
        return {
            "message_id": self.message_id,
            "time": str(datetime.datetime.now()),
            "case_num": self.case_num,
            "tech_id": self.tech_id,
            "lead_id": self.lead_id,
            "status": self.status,
            "severity_level": self.severity_level,
            "comments": self.comments
        }