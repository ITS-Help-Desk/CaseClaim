import datetime

import discord
import discord.ui as ui

from bot.models.outage import Outage
from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class EditOutageForm(ui.Modal, title='Outage Update Form'):
    def __init__(self, bot: "Bot", outage: Outage):
        """Creates a form for editing the fields of an outage.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            outage (Outage): The outage that is being edited
        """
        super().__init__()
        self.bot = bot
        self.outage = outage

        self.service = ui.TextInput(label='Service', style=discord.TextStyle.short, default=outage.service)
        self.add_item(self.service)
        self.parent_case = ui.TextInput(label='Parent Case # (Optional)', style=discord.TextStyle.short, required=False,
                                        default=outage.parent_case)
        self.add_item(self.parent_case)
        self.description = ui.TextInput(label='Description of Outage', style=discord.TextStyle.paragraph,
                                        default=outage.description)
        self.add_item(self.description)
        self.troubleshoot_steps = ui.TextInput(label='How to Troubleshoot (Optional)',
                                               style=discord.TextStyle.paragraph, required=False,
                                               default=outage.troubleshooting_steps)
        self.add_item(self.troubleshoot_steps)
        self.resolution_time = ui.TextInput(label='Expected Resolution Time (Optional)', style=discord.TextStyle.short,
                                            required=False, default=outage.resolution_time)
        self.add_item(self.resolution_time)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Once submitted, this edits the outage in the database and edits the case and announcement messages

        Args:
            interaction (discord.Interaction): The submit modal interaction
        """
        user = User.from_id(self.bot.connection, interaction.user.id)

        # Collect form information
        self.new_service = str(self.service)
        self.new_parent_case = str(self.parent_case) if len(str(self.parent_case)) != 0 else None
        self.new_description = str(self.description)
        self.new_troubleshoot_steps = str(self.troubleshoot_steps) if len(str(self.troubleshoot_steps)) != 0 else None
        self.new_resolution_time = str(self.resolution_time) if len(str(self.resolution_time)) != 0 else None

        if not self.validate_inputs():
            await interaction.response.send_message(content="Error! Please verify inputs aren't too large", ephemeral=True, delete_after=60)
            return

        self.outage.remove_from_database(self.bot.connection)

        new_outage = Outage(self.outage.message_id, self.outage.case_message_id, self.new_service, self.new_parent_case, self.new_description, self.new_troubleshoot_steps, self.new_resolution_time, self.outage.user, True)

        new_outage.add_to_database(self.bot.connection)

        # Create announcement embed
        announcement_embed = discord.Embed(colour=discord.Color.red())
        announcement_embed.set_author(name=f"{self.new_service}", icon_url="https://www.route66sodas.com/wp-content/uploads/2019/01/Alert.gif")

        try:
            announcement_embed.set_footer(text=user.full_name, icon_url=interaction.user.avatar.url)
        except:
            # Avatar not found
            announcement_embed.set_footer(text=user.full_name)

        announcement_embed.timestamp = datetime.datetime.now()

        # Add parent case
        if self.new_parent_case is not None and len(str(self.new_parent_case)) != 0:
            announcement_embed.description = f"Parent Case: **{self.new_parent_case}**"

        announcement_embed.add_field(name="Description", value=f"{self.new_description}", inline=False)

        # Add troubleshooting steps
        if self.new_troubleshoot_steps is not None and len(str(self.new_troubleshoot_steps)) != 0:
            announcement_embed.add_field(name="How to Troubleshoot", value=f"{self.new_troubleshoot_steps}", inline=False)

        # Add resolution time
        if self.new_resolution_time is not None and len(str(self.new_resolution_time)) != 0:
            announcement_embed.add_field(name="ETA to Resolution", value=f"{self.new_resolution_time}", inline=False)

        # Edit announcement message
        announcement_message: discord.Message = await interaction.channel.fetch_message(self.outage.message_id)
        await announcement_message.edit(embed=announcement_embed)

        # Create case embed
        case_embed = discord.Embed(title=f"{self.new_service}", colour=discord.Color.red())
        case_embed.description = f"{announcement_message.jump_url}"
        case_embed.set_footer()

        if self.new_parent_case is not None and len(str(self.new_parent_case)) != 0:
            case_embed.description += f"\nParent Case: **{self.new_parent_case}**"

        # Edit case message
        case_channel = await interaction.guild.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.fetch_message(self.outage.case_message_id)
        await case_message.edit(embed=case_embed)

        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=0)

    def validate_inputs(self) -> bool:
        if self.new_service is None or self.new_description is None:
            return False

        if self.new_parent_case is not None and len(str(self.new_parent_case)) > 255:
            return False

        if self.new_resolution_time is not None and len(str(self.new_resolution_time)) > 255:
            return False

        return True
