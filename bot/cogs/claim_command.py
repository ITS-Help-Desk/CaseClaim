from discord import app_commands
from discord.ext import commands
import discord
from datetime import datetime
from ..views.tech_view import TechView
from ..claim import Claim, InvalidClaimError

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class ClaimCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /claim command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot


    @app_commands.command(name="claim", description = "Claim cases using this command.")
    @app_commands.describe(case_num="Case #")
    async def claim(self, interaction: discord.Interaction, case_num: str):
        """Claims a case for a user, and sends a case claimed message into the
        case claims channel with buttons allowing the user to complete
        the case or unclaim the case.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
            case_num (str): The case number in Salesforce (e.g. "00960979")
        """
        # Ensure user is claiming case in the correct channel
        if interaction.channel.id != self.bot.cases_channel:
            claimed = discord.Embed(description=f"Cases cannot be claimed in this channel. Please go to <#{self.bot.cases_channel}>", colour=discord.Color.red())
            await interaction.response.send_message(embed=claimed, ephemeral=True,  delete_after=300)
            return

        # Create a Case object, checks to see if it's valid
        try:
            case = Claim(case_num=case_num, tech_id=interaction.user.id)
        except InvalidClaimError:
            invalid = discord.Embed(description=f"**{case_num}** is an invalid case number!", colour=discord.Color.red())
            await interaction.response.send_message(embed=invalid, ephemeral=True, delete_after=300)
            return
        
        # Check to see if the case claimed has already been claimed and is in progress.
        if self.bot.check_if_claimed(case.case_num):
            claimed = discord.Embed(description=f"**{case.case_num}** has already been claimed.", colour=discord.Color.red())
            await interaction.response.send_message(embed=claimed, ephemeral=True,  delete_after=300)
            return


        # User has claimed the case successfully, create the embed and techview.
        message_embed = discord.Embed(
            description=f"Is being worked on by <@{case.tech_id}>",
            colour=self.bot.embed_color,
            timestamp=datetime.now()
        )

        message_embed.set_author(name=f"{case.case_num}", icon_url=f'{interaction.user.display_avatar}')
        message_embed.set_footer(text="Claimed")

        message_view = TechView(self.bot)

        # Send message, add case to the list of cases
        await interaction.response.send_message(embed=message_embed, view=message_view)
        response = await interaction.original_response()
        case.message_id = response.id

        self.bot.add_case(case)