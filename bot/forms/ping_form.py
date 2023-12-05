import discord
import discord.ui as ui
from typing import Union
from datetime import datetime

from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback
from bot.models.pending_feedback import PendingFeedback
from bot.models.user import User

from bot.status import Status

from bot.views.affirm_view import AffirmView
from bot.helpers.other import is_working_time

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class PingForm(ui.Modal, title='Feedback Form'):
    def __init__(self, bot: "Bot", case: Union[CompletedClaim, CheckedClaim]):
        """Creates a feedback form for the LeadView whenever a lead would
        like to ping a case and provide feedback.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            case (Claim): The case object.
        """
        super().__init__()
        self.bot = bot
        self.case = case

    severity = ui.TextInput(label='Severity of Ping | Low Moderate High Critical', style=discord.TextStyle.short)
    description = ui.TextInput(label='Description of Issue', style=discord.TextStyle.paragraph)
    to_do = ui.TextInput(label='To Do (Optional)', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        original_user = await self.bot.fetch_user(self.case.tech.discord_id)

        # Send message
        await interaction.response.send_message(content="Pinged", ephemeral=True, delete_after=0)  # Acknowledge interaction, immediately delete message

        try:
            # Delete checker message
            await interaction.message.delete()
        except:
            pass

        # Update the lead if /ping is used (and a different lead is using it)
        if type(self.case) == CheckedClaim and self.case.lead.discord_id != interaction.user.id:
            self.case.update_lead(self.bot.connection, interaction.user.id)

        if is_working_time(interaction.created_at, self.bot.holidays):
            # During working time, send ping as normal
            fb_embed = discord.Embed(colour=discord.Color.red(), timestamp=datetime.now())

            fb_embed.description = f"<@{self.case.tech.discord_id}>, this case has been pinged by <@{interaction.user.id}>."

            fb_embed.add_field(name="Reason", value=str(self.description), inline=False)

            # Add a to-do message if none is passed in
            if len(str(self.to_do)) == 0:
                fb_embed.add_field(name="To Do",
                                   value="Review and let us know if you have any questions!",
                                   inline=False)
            else:
                fb_embed.add_field(name="To Do", value=str(self.to_do), inline=False)

            fb_embed.add_field(name="", value=str("*Note: Please review this information and take actions during work hours, not after!*"))

            fb_embed.set_author(name=f"{self.case.case_num}", icon_url=f'{original_user.display_avatar}')
            fb_embed.set_footer(text=f"{self.severity} severity level")

            # Create thread
            channel = interaction.user.guild.get_channel(self.bot.cases_channel)  # cases channel
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
            message = await thread.send(embed=fb_embed, view=AffirmView(self.bot))

            ping = Feedback(thread.id, message.id, str(self.severity), str(self.description))
            ping.add_to_database(self.bot.connection)

            if type(self.case) == CheckedClaim:
                self.case.add_ping_thread(self.bot.connection, ping.thread_id)
                self.case.change_status(self.bot.connection, Status.PINGED)
            elif type(self.case) == CompletedClaim:
                # Remove unpinged case from log
                self.case.remove_from_database(self.bot.connection)

                checked_case = CheckedClaim(self.case.checker_message_id, self.case.case_num, self.case.tech,
                                            User.from_id(self.bot.connection, interaction.user.id),
                                            self.case.claim_time,
                                            self.case.complete_time, datetime.now(), Status.PINGED, ping.thread_id)
                checked_case.add_to_database(self.bot.connection)

        else:
            # Not during work hours, create a PendingPing
            if type(self.case) == CheckedClaim:
                pending_ping = PendingFeedback(self.case.checker_message_id, str(self.severity), str(self.description), str(self.to_do))
                pending_ping.add_to_database(self.bot.connection)
            elif type(self.case) == CompletedClaim:
                # Remove CompletedClaim from log
                self.case.remove_from_database(self.bot.connection)

                # Add a CheckedClaim
                checked_case = CheckedClaim(self.case.checker_message_id, self.case.case_num, self.case.tech,
                                            User.from_id(self.bot.connection, interaction.user.id),
                                            self.case.claim_time,
                                            self.case.complete_time, datetime.now(), Status.PINGED, None)
                checked_case.add_to_database(self.bot.connection)

                # Add a PendingPing
                pending_ping = PendingFeedback(self.case.checker_message_id, str(self.severity), str(self.description), str(self.to_do))
                pending_ping.add_to_database(self.bot.connection)
