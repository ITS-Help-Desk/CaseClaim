import datetime


class InvalidCaseError(Exception):
    pass

class Case:
    case_num: str
    tech_id: int
    message_id: int
    status: str
    lead: int

    def __init__(self, case_num: str, tech_id: int):
        """Creates a Case class to store all information about a case

        Instance Variables:
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech_id (int): The Discord id of the tech who claimed the case
            message_id (int): The Discord id of the case claim message
            status (str): The status of the case after being reviewed
            lead (int): The Discord id of the lead who reviewed the case

        Args:
            case_num (str): The case number in Salesforce (e.g. "00960979")
            tech_id (int): The Discord id of the tech who claimed the case

        Raises:
            InvalidCaseError: When the case number provided isn't valid (e.g. case num isn't 8 digits).
        """
        self.tech_id = tech_id
        try:
            # Test if case_num is an 8 digit number
            if case_num == None or not case_num.isdigit() or len(case_num) != 8:
                raise ValueError()
            self.case_num = case_num
        except ValueError:
            raise InvalidCaseError("Invalid case provided!")  


    def log_format(self) -> list[str]:
        """Returns all of the information about the case in the format needed to log the case in log.csv

        Returns:
            list[str]: Returns a list in the format of [full_time, truncated_time, case_num, tech_id, status, lead_id]
        """
        timestamp = datetime.datetime.now()
        return [str(timestamp).split(' ')[0], str(timestamp).split(' ')[1][:5], self.case_num, str(self.tech_id), self.status, str(self.lead)]