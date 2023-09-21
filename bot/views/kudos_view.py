import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class KudosView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a view with a "Thanks!" button for a tech to press
        to acknowledge a Kudos message and delete the thread.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(emoji="✅", style=discord.ButtonStyle.primary, custom_id="thanks")
    async def button_thanks(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a tech, it deletes the Kudos thread.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.channel.delete()
        await interaction.response.defer(thinking=False)  # Acknowledge button press
