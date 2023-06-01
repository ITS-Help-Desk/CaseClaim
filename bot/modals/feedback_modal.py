import discord
import discord.ui as ui
from datetime import datetime
from ..claim import Claim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class FeedbackModal(ui.Modal, title='Feedback Form'):
    def __init__(self, bot: "Bot", case: Claim):
        """Creates a feedback form for the LeadView whenever a lead would
        like to ping a case and provide feedback.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            case (Claim): The case object.
        """
        super().__init__()
        self.bot = bot
        self.case = case

    severity = ui.TextInput(label='Severity of Ping | Low Moderate High Critical',style=discord.TextStyle.short)
    description = ui.TextInput(label='Description of Issue', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        original_user =  await self.bot.fetch_user(self.case.tech_id)
        
        fb_embed = discord.Embed(description=f"<@{self.case.tech_id}>, this case has been pinged by <@{interaction.user.id}>\n The reason for the ping is as follows:\n{self.description}",
                        colour=discord.Color.red(),
                        timestamp=datetime.now())
        fb_embed.set_author(name=f"{self.case.case_num}", icon_url=f'{original_user.display_avatar}')
        fb_embed.set_footer(text=f"{self.severity} severity level")

        channel = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel
        thread = await channel.create_thread(
            name=f"{self.case.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been pinged.",
            invitable=False
        )
    
        await thread.add_user(interaction.user)
        await thread.add_user(original_user)
        await thread.send(embed=fb_embed)
        await interaction.response.send_message(content="Pinged", delete_after=0)
        self.case.status = f"Pinged"
        self.case.severity_level = self.severity
        self.case.comments = self.description
        self.case.lead_id = interaction.user.id
        self.case.log()

        self.bot.remove_case(self.case.message_id)