from discord import app_commands
from discord.ext import commands
import discord
from datetime import datetime
import traceback

from bot.models.user import User
from bot.models.active_claim import ActiveClaim
from bot.models.announcement import Announcement
from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim

from bot.views.claim_view import ClaimView

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

    @app_commands.command(name="claim", description="Claim cases using this command.")
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
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return

        # Check if case_num is an 8-digit number
        if case_num is None or len(case_num) != 8 or not case_num.isdigit():
            msg = f"**{case_num}** is an invalid case number!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return

        # Check to see if the case claimed has already been claimed and is in progress.
        case = ActiveClaim.from_case_num(self.bot.connection, case_num)
        if case is not None:
            msg = f"**{case_num}** has already been claimed!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return

        # Check to see if user is in the list
        u = User.from_id(self.bot.connection, interaction.user.id)
        if u is None:
            msg = f"Please use the **/join** command before claiming cases."
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return


        # Check if it's been claimed in the last 15 minutes
        potential_cases: list[CompletedClaim, CheckedClaim] = CompletedClaim.get_all_with_case_num(self.bot.connection, case_num)
        checked = CheckedClaim.get_all_with_case_num(self.bot.connection, case_num)
        potential_cases.extend(checked)

        recent = False
        for case in potential_cases:
            if case.tech.discord_id == interaction.user.id:
                continue  # skip cases made by same user
            delta = datetime.now() - case.claim_time
            diff_mins = delta.total_seconds() / 60.0

            if diff_mins <= 15:
                # Send ephemeral
                await interaction.response.send_message(content=f"<@!{interaction.user.id}> WARNING: **{case_num}** was claimed by <@!{case.tech.discord_id}> in the last 15 minutes.",
                                                        ephemeral=True,
                                                        delete_after=180)
                recent = True
                break

        # User has claimed the case successfully, create the embed and techview.
        message_embed = discord.Embed(
            description=f"Is being worked on by <@{interaction.user.id}>",
            colour=self.bot.embed_color,
            timestamp=datetime.now()
        )
        message_embed.set_author(name=f"{case_num}", icon_url=f'{interaction.user.display_avatar}')
        message_embed.set_footer(text="Claimed")

        # Send message
        if not recent:
            # Respond to interaction
            await interaction.response.send_message(embed=message_embed, view=ClaimView(self.bot))
            response = await interaction.original_response()
            message_id = response.id
        else:
            # Send new message
            msg = await interaction.channel.send(embed=message_embed, view=ClaimView(self.bot))
            message_id = msg.id

        # Now that message has been sent, update the active cases
        # with the new message id
        tech = User.from_id(self.bot.connection, interaction.user.id)

        case = ActiveClaim(message_id, case_num, tech, datetime.now())
        case.add_to_database(self.bot.connection)

        self.bot.resend_outages = True
        await Announcement.resend(self.bot)

    @claim.error
    async def claim_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/claim** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(content=msg)
