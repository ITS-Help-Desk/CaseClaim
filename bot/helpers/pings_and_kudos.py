import datetime
import discord

from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback
from bot.models.pending_feedback import PendingFeedback

from bot.views.affirm_view import AffirmView
from bot.views.kudos_view import KudosView

from bot.status import Status


async def send_pending_ping(bot: 'Bot', pp: PendingFeedback, case_channel: discord.TextChannel):
    now = datetime.datetime.now()
    # Ping the case as normal
    claim = CheckedClaim.from_checker_message_id(bot.connection, pp.checker_message_id)
    claim.change_status(bot.connection, Status.PINGED)

    tech = await bot.fetch_user(claim.tech.discord_id)
    lead = await bot.fetch_user(claim.lead.discord_id)

    # During working time, send ping as normal
    fb_embed = discord.Embed(colour=discord.Color.red(), timestamp=now)

    fb_embed.description = f"<@{tech.id}>, this case has been pinged by <@{lead.id}>."

    fb_embed.add_field(name="Reason", value=str(pp.description), inline=False)

    # Add a to-do message if none is passed in
    if len(str(pp.to_do)) == 0:
        fb_embed.add_field(name="To Do",
                           value="Review and let us know if you have any questions!",
                           inline=False)
    else:
        fb_embed.add_field(name="To Do", value=str(pp.to_do), inline=False)

    fb_embed.add_field(name="", value=str("*Note: Please review this information and take actions during work hours, not after!*"))
    fb_embed.set_author(name=f"{claim.case_num}", icon_url=f'{tech.display_avatar}')
    fb_embed.set_footer(text=f"{pp.severity} severity level")

    # Create thread
    thread = await case_channel.create_thread(
        name=f"{claim.case_num}",
        message=None,
        auto_archive_duration=4320,
        type=discord.ChannelType.private_thread,
        reason="Case has been pinged.",
        invitable=False
    )

    # Add users to thread and send message
    await thread.add_user(tech)
    await thread.add_user(lead)
    message = await thread.send(embed=fb_embed, view=AffirmView(bot))

    # Create ping object
    ping = Feedback(thread.id, message.id, str(pp.severity), str(pp.description))
    ping.add_to_database(bot.connection)
    claim.add_ping_thread(bot.connection, thread.id)

    # Remove pending ping
    pp.remove_from_database(bot.connection)


async def send_pending_kudos(bot: 'Bot', pp: PendingFeedback, case_channel: discord.TextChannel):
    now = datetime.datetime.now()
    claim = CheckedClaim.from_checker_message_id(bot.connection, pp.checker_message_id)
    tech = await bot.fetch_user(claim.tech.discord_id)

    fb_embed = discord.Embed(
        description=f"<@{tech.id}>, this case has been complimented by <@{tech.id}>.",
        colour=discord.Color.green(),
        timestamp=now
    )

    fb_embed.add_field(name="Description", value=str(pp.description), inline=False)

    fb_embed.set_author(name=f"{claim.case_num}", icon_url=f'{tech.display_avatar}')

    # Create thread
    thread = await case_channel.create_thread(
        name=f"{claim.case_num}",
        message=None,
        auto_archive_duration=4320,
        type=discord.ChannelType.private_thread,
        reason="Case has been complimented 😁",
        invitable=False
    )

    # Add user to thread and send message
    await thread.add_user(tech)
    message = await thread.send(embed=fb_embed, view=KudosView(bot))

    # Add a Ping class to store the kudos comment data
    kudo = Feedback(thread.id, message.id, "Kudos", str(pp.description))
    kudo.add_to_database(bot.connection)

    claim.add_ping_thread(bot.connection, kudo.thread_id)

    # Remove PendingPing
    pp.remove_from_database(bot.connection)
