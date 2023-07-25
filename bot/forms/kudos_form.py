import discord
import discord.ui as ui
from datetime import datetime

from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
from bot.status import Status

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class KudosForm(ui.Modal, title='Kudos Form'):
    def __init__(self, bot: "Bot", case: CompletedClaim):
        super().__init__()
        self.bot = bot
        self.case = case

    description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        original_user = await self.bot.fetch_user(self.case.tech.discord_id)

        fb_embed = discord.Embed(
            description=f"<@{self.case.tech.discord_id}>, this case has been complimented by <@{interaction.user.id}>.",
            colour=discord.Color.green(),
            timestamp=datetime.now())

        fb_embed.add_field(name="Description", value=str(self.description), inline=False)

        fb_embed.set_author(name=f"{self.case.case_num}", icon_url=f'{original_user.display_avatar}')

        # Create thread
        channel = interaction.user.guild.get_channel(self.bot.cases_channel)  # cases channel
        thread = await channel.create_thread(
            name=f"{self.case.case_num}",
            message=None,
            auto_archive_duration=4320,
            type=discord.ChannelType.private_thread,
            reason="Case has been complimented 😁",
            invitable=False
        )

        # Add users to thread and send message
        await thread.add_user(interaction.user)
        await thread.add_user(original_user)
        message = await thread.send(embed=fb_embed)

        # Send message
        await interaction.response.send_message(content="Complemented!",
                                                delete_after=0)  # Acknowledge interaction, immediately delete message
        # Remove unpinged case from log
        self.case.remove_from_database(self.bot.connection)

        checked_case = CheckedClaim(self.case.checker_message_id, self.case.case_num, self.case.tech,
                                    User.from_id(self.bot.connection, interaction.user.id), self.case.claim_time,
                                    self.case.complete_time, datetime.now(), Status.KUDOS, None)
        checked_case.add_to_database(self.bot.connection)

        # Delete checker message
        await interaction.message.delete()
