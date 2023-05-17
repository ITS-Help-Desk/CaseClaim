import discord
import discord.ui as ui
from datetime import datetime
import random
from .lead import LeadView
from ..case import Claim

from typing import Union
# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class TechView(ui.View):
    def __init__(self, bot: "Bot", original_user: Union[discord.User, discord.Member], case: Claim):
        """Creates the case claim embed with the Complete and Unclaim buttons. Also sends a
        embed to the lead claims channel with a LeadView embed.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            original_user (Union[discord.User, discord.Member]): The user who sent the command to show the TechView.
            case (Claim): The case object.
        """
        super().__init__(timeout=None)
        self.bot = bot
        self.original_user = original_user #tech that claimed the case
        self.case = case

    #if the user is the same as the claimer, 
    @ui.button(label="Complete", style=discord.ButtonStyle.success)
    async def button_claim(self, interaction: discord.Interaction, button):
        if(self.original_user == interaction.user):
            channel = interaction.user.guild.get_channel(self.bot.claims_channel) #claims channel
            if random.random() < 1:   #percentage of cases sent to claims
                #send a message in the claims channel and add the lead view to it.
                    lead_embed = discord.Embed(description=f"Has been marked as complete by <@{self.original_user.id}>",
                                                colour=discord.Color.teal(),
                                                timestamp=datetime.now())
                    lead_embed.set_author(name=f"{self.case.case_num}",icon_url=f'{self.original_user.display_avatar}')
                    lead_embed.set_footer(text="Completed")
                    await channel.send(embed=lead_embed, view=LeadView(self.bot, self.original_user,self.case))
            
            # Update case information
            self.case.status = "Complete"
            self.case.lead_id = self.bot.user.id

            self.case.log()

            self.bot.remove_case(interaction.message.id)
            await interaction.message.delete()

            completed_embed = discord.Embed(description=f"Has been marked complete by <@{self.original_user.id}>",
                                                colour=discord.Color.green(),
                                                timestamp=datetime.now())
            completed_embed.set_author(name=f"{self.case.case_num}",icon_url=f'{self.original_user.display_avatar}')
            completed_embed.set_footer(text="Completed")
            channel2 = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel
            await interaction.response.send_message(embed=completed_embed, ephemeral=True)
            
        else:
            not_yours = discord.Embed(description=f"{interaction.user}, you didn't claim this case!",
                colour=discord.Color.yellow())
            await interaction.response.send_message(embed=not_yours, ephemeral=True, delete_after=300)
            
    #if the user is the same as the claimer or is a lead, then deletes, else responds with error
    @ui.button(label="Unclaim", style=discord.ButtonStyle.secondary)
    async def button_unclaim(self, interaction: discord.Interaction, button):
        guild = interaction.message.guild
        lead_role = discord.utils.get(guild.roles, name="Lead")
        if(self.original_user == interaction.user or lead_role in interaction.user.roles):
            self.bot.remove_case(interaction.message.id)
            await interaction.message.delete()
        else:
            not_yours = discord.Embed(description=f"{interaction.user}, you didn't claim this case!",
                colour=discord.Color.yellow())
            await interaction.response.send_message(embed=not_yours, ephemeral=True, delete_after=300)
            return