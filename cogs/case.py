import datetime
import csv


class InvalidCaseError(Exception):
    pass

class Case:
    log_file_path: str # Passed in during instantiation of Bot

    def __init__(self, case_num: str, tech_id: int):
        """Creates a Case class to store all information about a case

        Instance Variables:
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech_id (int): The Discord id of the tech who claimed the case
            message_id (int): The Discord id of the case claim message
            status (str): The status of the case ("Completed"/"Checked"/"Flagged")
            lead (int): The Discord id of the lead who reviewed the case
            flag_severity (str): The severity of the flag (if flagged)
            comments (str): The comments of the flag (if flagged)

        Args:
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech_id (int): The Discord id of the tech who claimed the case

        Raises:
            InvalidCaseError: When the case number provided isn't valid (e.g. case num isn't 8 digits).
        """
        try:
            # Test if case_num is an 8 digit number
            if case_num == None or not case_num.isdigit() or len(case_num) != 8:
                raise ValueError()
            self.case_num = case_num
        except ValueError:
            raise InvalidCaseError("Invalid case provided!")
        
        self.tech_id: int = tech_id
        # Define the rest of the instance vars with placeholder values
        self.message_id: int = -1
        self.status: str = ""
        self.lead_id: int = -1
        self.flag_severity = ""
        self.comments = ""


    def log(self) -> None:
        """Logs the case to the logfile."""
        
        with open(self.log_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.log_format())

    def log_format(self) -> list[str]:
        """Returns all of the information about the case in the format needed to log the case in log.csv

        Returns:
            list[str]: Returns a list in the format of message_id, timestamp, case_num, tech_user_ID, lead_user_ID, status, flag_severity, comments
        """
        return [
            self.message_id,
            str(datetime.datetime.now()),
            self.case_num,
            self.tech_id,
            self.lead_id,
            self.status,
            self.flag_severity,
            self.comments
        ]