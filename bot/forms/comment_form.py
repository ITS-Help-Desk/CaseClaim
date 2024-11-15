import discord
import discord.ui as ui
from datetime import datetime

from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
from bot.models.feedback import Feedback

from bot.status import Status
from bot.views.kudos_view import KudosView


# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class CommentForm(ui.Modal, title='Comment Form'):
    def __init__(self, bot: "Bot", case: CompletedClaim):
        """Creates a feedback form for internal feedback on a tech's handling of a case.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            case (CompletedClaim): The claim that is being commented on
        """
        super().__init__()
        self.bot = bot
        self.case = case

    description = ui.TextInput(label='Description', required=False, style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        """Adds a comment to the database, but doesn't make a thread to display
        it to the technician.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        # Send message
        await interaction.response.send_message(content=":thumbsup:", ephemeral=True, delete_after=0)  # Acknowledge interaction, immediately delete message

        # Delete checker message
        await interaction.message.delete()

        if len(str(self.description)) == 0:
            comment_thread = None
        else:
            # Add a Feedback class to store the comment data
            comment = Feedback(interaction.message.id, interaction.message.id, "Comment", str(self.description))
            comment.add_to_database(self.bot.connection)

            comment_thread = comment.thread_id

        # Remove unpinged case from log
        self.case.remove_from_database(self.bot.connection)

        checked_case = CheckedClaim(self.case.checker_message_id, self.case.case_num, self.case.tech,
                                    User.from_id(self.bot.connection, interaction.user.id), self.case.claim_time,
                                    self.case.complete_time, datetime.now(), Status.CHECKED, comment_thread)
        
        checked_case.add_to_database(self.bot.connection)

