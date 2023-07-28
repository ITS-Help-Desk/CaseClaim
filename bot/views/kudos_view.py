import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class KudosView(ui.View):
    def __init__(self, bot: "Bot"):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Thanks!", style=discord.ButtonStyle.primary, custom_id="thanks")
    async def button_thanks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()
        await interaction.response.defer(thinking=False)  # Acknowledge button press
