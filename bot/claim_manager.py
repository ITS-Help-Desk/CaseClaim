import json
from typing import Any, Optional
from bot.claim import Claim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class ClaimManager:
    active_claims: dict[int, Claim]

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.active_claims = {}
        self.load_claims()
    

    def add_claim(self, case: Claim, store=True) -> None:
        """Adds a case to the list of actively worked on cases.

        Args:
            case (Claim): The case that is being added
            store (bool): Whether or not to store on file (defaults to True).
        """
        if case.message_id == None:
            raise ValueError("Case message ID not provided!")
        
        self.active_claims[case.message_id] = case
        if store:
            self.store_claims()
    

    def get_claim(self, message_id: int) -> Optional[Claim]:
        """Gets a case from the list of actively worked-on cases.

        Args:
            message_id (int): The id of the original message the bot responded with.

        Returns:
            Optional[Claim]: The claim (if it exists).
        """
        return self.active_claims.get(message_id, None)
    

    def check_if_claimed(self, case_num: str) -> bool:
        """Checks if a case has already been claimed or not by
        looking it up in the active_claims dict.

        Args:
            case_num (str): The number of the case trying to be claimed

        Returns:
            bool: True or False if the case has been claimed or not
        """
        for message_id in list(self.active_claims.keys()):
            case = self.active_claims[message_id]
            if case.case_num == case_num and case.status != "Complete":
                return True
        return False
    

    def remove_claim(self, message_id: int) -> None:
        """Removes a case from the list of actively worked on cases.

        Args:
            message_id (int): The message id of the case that is being removed.
        """
        try:
            del self.active_claims[message_id]
        except KeyError:
            pass
        self.store_claims()
    

    def store_claims(self) -> None:
        """Stores the actively worked on cases into the file actives_cases.json
        """
        new_data = {}
        for message_id in self.active_claims.keys():
            c = self.get_claim(message_id)
            if c is not None:
                new_data[str(message_id)] = c.json_format()
        with open('active_cases.json', 'w') as f:
            json.dump(new_data, f)
    

    def load_claims(self) -> None:
        """Loads the actively worked on cases from the file active_cases.json
        """
        self.active_claims = {}
        with open('active_cases.json', 'r') as f:
            new_data: dict[str, Any] = json.load(f)
            for message_id in new_data.keys():
                c = Claim.load_from_json(new_data[message_id])
                self.active_claims[int(message_id)] = c