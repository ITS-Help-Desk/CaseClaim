import discord
import discord.ui as ui
from datetime import datetime

from bot.views.ping_view import PingView
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
    to_do = ui.TextInput(label='To Do (Optional)', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        original_user = await self.bot.fetch_user(self.case.tech_id)
        
        fb_embed = discord.Embed(description=f"<@{self.case.tech_id}>, this case has been pinged by <@{interaction.user.id}>.",
                        colour=discord.Color.red(),
                        timestamp=datetime.now())

        fb_embed.add_field(name="Reason", value=str(self.description), inline=False)

        # Add a to-do message if none is passed in
        if len(str(self.to_do)) == 0:
            fb_embed.add_field(name="To Do", value="Please review these details and let us know if you have any questions!", inline=False)
        else:
            fb_embed.add_field(name="To Do", value=str(self.to_do), inline=False)
        
        fb_embed.set_author(name=f"{self.case.case_num}", icon_url=f'{original_user.display_avatar}')
        fb_embed.set_footer(text=f"{self.severity} severity level")

        # Create thread
        channel = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel
        thread = await channel.create_thread(
            name=f"{self.case.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been pinged.",
            invitable=False
        )

        # Add users to thread and send message
        await thread.add_user(interaction.user)
        await thread.add_user(original_user)
        message = await thread.send(embed=fb_embed, view=PingView(self.bot))

        # Send message
        await interaction.response.send_message(content="Pinged", delete_after=0) # Acknowledge interaction, immediately delete message

        # Update case, re-log it
        old_message_id = self.case.message_id
        self.case.message_id = message.id
        self.case.status = "Pinged"
        self.case.severity_level = str(self.severity)
        self.case.comments = str(self.description)
        self.case.lead_id = interaction.user.id

        self.case.log()

        self.bot.remove_case(old_message_id)