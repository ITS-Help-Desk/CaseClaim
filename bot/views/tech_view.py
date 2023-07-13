import discord
import discord.ui as ui
from datetime import datetime
import random
from .lead_view import LeadView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class TechView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates the case claim embed with the Complete and Unclaim buttons. Also sends a
        embed to the lead claims channel with a LeadView embed.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    
    @ui.button(label="Complete", style=discord.ButtonStyle.success, custom_id='complete')
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a tech, it marks the case as complete and allows a lead to review it.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        self.case = self.bot.claim_manager.get_claim(interaction.message.id)

        if self.case.tech_id == interaction.user.id:
            # Update case information
            self.case.status = "Complete"

            self.bot.claim_manager.remove_claim(interaction.message.id)
            self.case.submitted_time = datetime.now()
            await interaction.message.delete()

            completed_embed = discord.Embed(description=f"Has been marked complete by <@{interaction.user.id}>",
                                                colour=discord.Color.green(),
                                                timestamp=datetime.now())
            completed_embed.set_author(name=f"{self.case.case_num}",icon_url=f'{interaction.user.display_avatar}')
            completed_embed.set_footer(text="Completed")
            await interaction.response.send_message(embed=completed_embed, ephemeral=True)

            # Send a message in the claims channel and add the lead view to it.
            if random.random() < self.bot.review_rate: #percentage of cases sent to claims
                channel = interaction.user.guild.get_channel(self.bot.claims_channel) #claims channel
                lead_embed = discord.Embed(description=f"Has been marked as complete by <@{self.case.tech_id}>",
                                            colour=self.bot.embed_color,
                                            timestamp=datetime.now())
                lead_embed.set_author(name=f"{self.case.case_num}",icon_url=f'{interaction.user.display_avatar}')
                lead_embed.set_footer(text="Completed")
                msg = await channel.send(embed=lead_embed, view=LeadView(self.bot))

                # Add the case back into active_cases with a different key
                # This allows the leadview to be persistent
                self.case.message_id = msg.id
                self.bot.claim_manager.add_claim(self.case)
            else:
                # If case isn't sent for review, log it
                self.case.log()
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
        self.case = self.bot.claim_manager.get_claim(interaction.message.id)

        if self.case.tech_id == interaction.user.id or self.bot.check_if_lead(interaction.user):
            self.bot.claim_manager.remove_claim(interaction.message.id)
            await interaction.message.delete()
        else:
            msg = f"<@!{interaction.user.id}>, you didn't claim this case!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)