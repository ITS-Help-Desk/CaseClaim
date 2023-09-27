import discord
import discord.ui as ui
from datetime import datetime

from bot.views.check_view import CheckView
from bot.views.force_complete_view import ForceCompleteView

from bot.models.active_claim import ActiveClaim
from bot.models.completed_claim import CompletedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ClaimView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates the case claim embed with the Complete and Unclaim buttons. Also sends a
        embed to the lead claims channel with a LeadView embed.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Complete", style=discord.ButtonStyle.success, custom_id='complete')
    async def button_complete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a tech, it marks the case as complete and allows a lead to review it.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = ActiveClaim.from_id(self.bot.connection, interaction.message.id)

        if case is None:
            await interaction.response.send_message("Error, please try again.", ephemeral=True, delete_after=300)

            raise AttributeError(f"Case is none (message ID: {interaction.message.id})")

        if case.tech.discord_id == interaction.user.id:
            case.remove_from_database(self.bot.connection)
            await interaction.message.delete()

            completed_embed = discord.Embed(description=f"Case has been marked complete, to view all your cases use **/mycases**",
                                            colour=discord.Color.green(),
                                            timestamp=datetime.now())
            completed_embed.set_author(name=f"{case.case_num}", icon_url=f'{interaction.user.display_avatar}')
            completed_embed.set_footer(text="Completed")
            await interaction.response.send_message(embed=completed_embed, ephemeral=True, delete_after=300)

            # Send a message in the claims channel and add the lead view to it.
            channel = interaction.user.guild.get_channel(self.bot.claims_channel)  # claims channel
            lead_embed = discord.Embed(description=f"Has been marked as complete by <@{case.tech.discord_id}>",
                                       colour=self.bot.embed_color,
                                       timestamp=datetime.now())
            lead_embed.set_author(name=f"{case.case_num}", icon_url=f'{interaction.user.display_avatar}')
            lead_embed.set_footer(text="Completed")
            msg = await channel.send(embed=lead_embed, view=CheckView(self.bot))

            # Add case to CompletedClaims
            completed_claim = CompletedClaim(msg.id, case.case_num, case.tech, case.claim_time, datetime.now())
            completed_claim.add_to_database(self.bot.connection)
        elif self.bot.check_if_lead(interaction.user):
            # Lead force completes a case
            await interaction.response.send_message(content=f"**{case.case_num}** Are you sure you'd like to force complete this case?", view=ForceCompleteView(self.bot), ephemeral=True, delete_after=30)
        else:
            # Wrong user presses button
            msg = f"<@!{interaction.user.id}>, you didn't claim this case!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)

    @ui.button(label="Unclaim", style=discord.ButtonStyle.secondary, custom_id='unclaim')
    async def button_unclaim(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a tech, it unclaims the case and allows other techs to claim it.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = ActiveClaim.from_id(self.bot.connection, interaction.message.id)

        if case.tech.discord_id == interaction.user.id or self.bot.check_if_lead(interaction.user):
            case.remove_from_database(self.bot.connection)
            await interaction.message.delete()
        else:
            msg = f"<@!{interaction.user.id}>, you didn't claim this case!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
