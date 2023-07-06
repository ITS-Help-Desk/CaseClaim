import json
from bot.announcement import Announcement

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class AnnouncementManager:
    announcements: list[Announcement]
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.announcements = []
        self.load_announcements()
    

    def get_announcement(self, announcement_message_id: int):
        for ann in self.announcements:
            if ann.announcement_message_id == announcement_message_id:
                return ann


    def add_announcement(self, outage: Announcement):
        self.announcements.append(outage)
        self.store_announcements()

    
    def remove_announcement(self, outage: Announcement):
        self.announcements.remove(outage)
        self.store_announcements()
    

    def store_announcements(self) -> None:
        data = {}

        for ann in self.announcements:
            data[ann.announcement_message_id] = ann.to_dict()
        
        with open("announcements.json", "w") as f:
            json.dump(data, f)


    def load_announcements(self) -> None:
        with open("announcements.json", "r") as f:
            data = json.load(f)
        
        for key in data.keys():
            if data[key]["type"] == "outage":
                outage = Announcement("outage", data[key]["info"])
        
                outage.announcement_message_id = int(key)
                self.announcements.append(outage)
            else:
                pass

    
    async def resend_announcements(self) -> None:
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
            else:
                pass