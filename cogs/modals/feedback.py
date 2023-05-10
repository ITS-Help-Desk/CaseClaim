import discord
import discord.ui as ui
from datetime import datetime
from ..case import Case

from typing import Union
# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class FeedbackModal(ui.Modal, title='Feedback Form'):
    def __init__(self, bot: "Bot", original_user: Union[discord.User, discord.Member], case: Case):
        """Creates a feedback form for the LeadView whenever a lead would
        like to flag a case and provide feedback.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            original_user (Union[discord.User, discord.Member]): The user who sent the command to show the TechView.
            case_num (Case): The case object.
        """
        super().__init__()
        self.bot = bot
        self.original_user = original_user #tech that originally claimed the case
        self.case = case

    severity = ui.TextInput(label='Severity of Flag | Low Moderate High Critical',style=discord.TextStyle.short)
    description = ui.TextInput(label='Description of Issue', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        fb_embed = discord.Embed(description=f"<@{self.original_user.id}>, this case has been flagged by <@{interaction.user.id}>\n The reason for the flag is as follows:\n{self.description}",
                        colour=discord.Color.yellow(),
                        timestamp=datetime.now())
        fb_embed.set_author(name=f"{self.case.case_num}",icon_url=f'{self.original_user.display_avatar}')
        fb_embed.set_footer(text=f"{self.severity} severity flag")

        channel = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel
        thread = await channel.create_thread(
            name=f"{self.case.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been flagged.",
            invitable=False
        )
    
        await thread.add_user(interaction.user)
        await thread.add_user(self.original_user)
        await thread.send(embed=fb_embed)
        await interaction.response.send_message(content="Flagged", delete_after=0)
        self.case.status = f"Flagged"
        self.case.flag_severity = self.severity
        self.case.comments = self.description
        self.case.lead_id = interaction.user.id
        self.case.log()