import json
from bot.announcement import Announcement
import time
from typing import Optional

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class AnnouncementManager:
    announcements: list[Announcement]
    def __init__(self, bot: "Bot"):
        """Creates the AnnouncementManager by loading
        all announcements from the announcements.json file

        Args:
            bot (Bot): A reference to the Bot class
        """
        self.bot = bot
        self.announcements = []
        self.load_announcements()
    

    def get_announcement(self, announcement_message_id: int) -> Optional[Announcement]:
        """Gets an announcement from the self.announcements list by its
        #announcements channel message ID


        Args:
            announcement_message_id (int): The message ID from the #announcements channel

        Returns:
            Optional[Announcement]: The announcement (if it can be found)
        """
        for ann in self.announcements:
            if ann.announcement_message_id == announcement_message_id:
                return ann


    def add_announcement(self, announcement: Announcement):
        """Adds an announcement from the self.announcements list and stores it in
        the announcements.json file

        Args:
            announcement (Announcement): The announcement object
        """
        self.announcements.append(announcement)
        self.store_announcements()

    
    def remove_announcement(self, announcement: Announcement):
        """Removes an announcement from the self.announcements list and stores it in
        the announcements.json file

        Args:
            announcement (Announcement): The announcement object
        """
        self.announcements.remove(announcement)
        self.store_announcements()
    

    def store_announcements(self) -> None:
        """Stores the announcements from the self.announcements list to
        the announcements.json file
        """
        data = {}

        for ann in self.announcements:
            data.update(ann.to_dict())
        
        with open("announcements.json", "w") as f:
            json.dump(data, f)


    def load_announcements(self) -> None:
        """Loads all of the announcements from the announcements.json
        file and stores them in the self.announcements list
        """
        with open("announcements.json", "r") as f:
            data = json.load(f)
        
        for key in data.keys():
            if data[key]["type"] == "outage":
                outage = Announcement("outage", data[key]["info"])
        
                outage.announcement_message_id = int(key)
                self.announcements.append(outage)
            elif data[key]["type"] == "announcement":
                announcement = Announcement("announcement", data[key]["info"])
        
                announcement.announcement_message_id = int(key)
                self.announcements.append(announcement)

    
    async def resend_announcements(self) -> None:
        """Resends any outages to the cases channel and
        deletes all old announcements from the cases channel
        """
        for ann in self.announcements:
            if ann.announcement_type == "outage":
                announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)
                announcement_message = await announcement_channel.fetch_message(ann.announcement_message_id)

                case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
                case_message = await case_channel.fetch_message(ann.info["case_message_id"])

                new_message = await case_channel.send(embed=ann.to_case_embed(announcement_message.jump_url), silent=True)
                await case_message.delete()

                ann.info["case_message_id"] = int(new_message.id)

                self.store_announcements()
            elif ann.announcement_type == "announcement":
                current = time.time()
                if current > ann.info["time"]:
                    announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)
                    announcement_message = await announcement_channel.fetch_message(ann.announcement_message_id)

                    announcement_embed = announcement_message.embeds[0]
                    announcement_embed.colour = self.bot.embed_color
                    await announcement_message.edit(content="", embed=announcement_embed)

                    case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
                    case_message = await case_channel.fetch_message(ann.info["case_message_id"])
                    await case_message.delete()

                    self.remove_announcement(ann)
