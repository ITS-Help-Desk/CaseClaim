import discord
import discord.ui as ui

from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class JoinForm(ui.Modal, title='Join Form'):
    def __init__(self, bot: "Bot"):
        """Creates a feedback form for the adding a user to the Users table.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__()
        self.bot = bot

    first_name = ui.TextInput(label='First Name', style=discord.TextStyle.short)
    last_name = ui.TextInput(label='Last Name', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        """Records the user's first and last name and saves it to the database.

        Args:
            interaction (discord.Interaction): The submit modal interaction
        """
        user = User(interaction.user.id, str(self.first_name), str(self.last_name))
        user.add_to_database(self.bot.connection)

        await interaction.response.send_message(content="👍",
                                                delete_after=0)  # Acknowledge interaction, immediately delete message
