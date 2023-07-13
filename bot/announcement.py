import discord


class Announcement:
    announcement_message_id: int
    def __init__(self, announcement_type: str, info: dict[str, str]):
        self.announcement_type = announcement_type
        self.info = info
    

    def to_dict(self) -> dict[str, str]:
        data = {}

        data[str(self.announcement_message_id)] = {
            "type": str(self.announcement_type),
            "info": self.info
        }

        return data


    def to_announcement_embed(self) -> discord.Embed:
        if self.announcement_type == "outage":
            service = self.info["service"]
            description = self.info["description"]
            parent_case = self.info["parent_case"]
            troubleshooting_steps = self.info["troubleshooting_steps"]
            resolution_time = self.info["resolution_time"]


            announcement_embed = discord.Embed(title=f"{service} Outage", colour=discord.Color.red())

            # Add parent case
            if parent_case is not None and len(str(parent_case)) != 0:
                announcement_embed.description = f"Parent Case: **{parent_case}**"
            
            announcement_embed.add_field(name="Description", value=f"{description}", inline=False)

            if troubleshooting_steps is not None and len(str(troubleshooting_steps)) != 0:
                announcement_embed.add_field(name="How to Troubleshoot", value=f"{troubleshooting_steps}", inline=False)

            if troubleshooting_steps is not None and len(str(resolution_time)) != 0:
                announcement_embed.add_field(name="ETA to Resolution", value=f"{resolution_time}", inline=False)
            
            return announcement_embed
        elif self.announcement_type == "announcement":
            title = self.info["title"]
            description = self.info["description"]

            announcement_embed = discord.Embed(title=title, colour=discord.Color.red())
            announcement_embed.description = description

            return announcement_embed

    def to_case_embed(self, announcement_message_jump_url: str) -> discord.Embed:
        if self.announcement_type == "outage":
            service = self.info["service"]
            parent_case = self.info["parent_case"]

            # Create case embed
            case_embed = discord.Embed(title=f"{service} Outage", colour=discord.Color.red())
            case_embed.description = f"{announcement_message_jump_url}"

            if parent_case is not None and len(str(parent_case)) != 0:
                case_embed.description += f"\nParent Case: **{parent_case}**"

            return case_embed
        elif self.announcement_type == "announcement":
            return self.to_announcement_embed()