from discord import app_commands
from discord.ext import commands
import discord
from datetime import datetime
from ..views.tech_view import TechView
from ..claim import Claim, InvalidClaimError
import traceback

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
        if interaction.channel_id != self.bot.cases_channel:
            msg = f"Cases cannot be claimed in this channel. Please go to <#{self.bot.cases_channel}>"
            await interaction.response.send_message(content=msg, ephemeral=True,  delete_after=300)
            return

        # Create a Case object, checks to see if it's valid
        try:
            case = Claim(case_num=case_num, tech_id=interaction.user.id)
        except InvalidClaimError:
            msg = f"**{case_num}** is an invalid case number!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return
        
        # Check to see if the case claimed has already been claimed and is in progress.
        if self.bot.check_if_claimed(case.case_num):
            msg = f"**{case.case_num}** has already been claimed."
            await interaction.response.send_message(content=msg, ephemeral=True,  delete_after=300)
            return
        
        # Temporarily add case using the interaction id
        # To prevent double claims
        case.message_id = interaction.id
        self.bot.add_case(case, store=False)
        
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

        # Now that message has been sent, update the active cases
        # with the new message id
        case.message_id = response.id
        self.bot.add_case(case)
        self.bot.remove_case(interaction.id)
    

    @claim.error
    async def claim_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)
        await ch.send(f"Error with **/claim** ran by <@!{ctx.user.id}>.\n```{full_error}```")