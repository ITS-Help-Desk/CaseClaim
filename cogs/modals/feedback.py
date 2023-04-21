import discord
import discord.ui as ui
from datetime import datetime


class FeedbackModal(ui.Modal, title='Feedback Form'):
    def __init__(self, bot, original_user, case_num):
        super().__init__()
        self.bot = bot
        self.original_user = original_user #tech that originally claimed the case
        self.case_num = case_num           #case number that tech claimed

    severity = ui.TextInput(label='Severity of Flag | Low Moderate High Critical',style=discord.TextStyle.short)
    description = ui.TextInput(label='Description of Issue', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        fb_embed = discord.Embed(description=f"<@{self.original_user.id}>, this case has been flagged by <@{interaction.user.id}>\n The reason for the flag is as follows:\n{self.description}",
                        colour=discord.Color.yellow(),
                        timestamp=datetime.now())
        fb_embed.set_author(name=f"{self.case_num}",icon_url=f'{self.original_user.display_avatar}')
        fb_embed.set_footer(text=f"{self.severity} severity flag")

        channel = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel
        thread = await channel.create_thread(name=f"{self.case_num}",
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
        self.bot.log_case(datetime.now(),self.case_num,f"Flagged, Reason: {self.description}",interaction.user.display_name,self.original_user.display_name)