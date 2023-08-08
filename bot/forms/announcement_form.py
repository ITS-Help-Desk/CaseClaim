import discord
import discord.ui as ui
import datetime

from bot.models.user import User
from bot.models.announcement import Announcement

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class AnnouncementForm(ui.Modal, title='Announcement Form'):
    def __init__(self, bot: "Bot"):
        super().__init__()
        self.bot = bot

    a_title = ui.TextInput(label='Title', style=discord.TextStyle.short)
    description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates an announcement message which will be sent to the #announcements channel along with
        a message that will be sent to the cases channel

        Args:
            interaction (discord.Interaction): The submit modal interaction
        """
        # Create announcement for AnnouncementManager
        a_title = str(self.a_title)
        description = str(self.description)
        days = 4

        end_date = datetime.datetime.now() + datetime.timedelta(days=days)

        # Create announcement embed
        announcement_embed = discord.Embed(title=a_title, colour=discord.Color.yellow())
        announcement_embed.description = description

        # Send announcement message
        announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)
        announcement_message = await announcement_channel.send(content="@here", embed=announcement_embed)

        # Send case message
        case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.send(embed=announcement_embed, silent=True)

        announcement = Announcement(announcement_message.id, case_message.id, a_title, description,
                                    User.from_id(self.bot.connection, interaction.user.id), end_date, True)

        announcement.add_to_database(self.bot.connection)

        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=0)

        await announcement_message.edit(content="")
