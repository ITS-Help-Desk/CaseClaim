from discord import app_commands
from discord.ext import commands
import discord
from datetime import datetime
from .views.tech import TechView


class Claim(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @app_commands.command(name="claim", description = "Claim cases using this command.")
    @app_commands.describe(case_num="Case #")
    async def claim(self, interaction: discord.Interaction, case_num: str):
        #defining the cases channel and the claims channel
        channel = interaction.user.guild.get_channel(self.bot.cases_channel) #cases channel

        #check to see if the number entered is an 8 digit number
        if not case_num.isdigit() or len(case_num) != 8:
            invalid = discord.Embed(description=f"{case_num} is an invalid case number!",
                                colour=discord.Color.yellow())
            await interaction.response.send_message(embed=invalid, ephemeral=True, delete_after=300)
            return

        #check to see if the case claimed has already been claimed and is in progress.
        async for message in channel.history(limit=50):
            if message.author == self.bot.user: #checks to see if the bot sent the message
                try:
                    embed = message.embeds[0]    #looks at the first embed
                    if embed != None:
                        if f"{case_num}" in embed.author.name and "Claimed" == embed.footer.text:
                            previous_tech = embed.description[embed.description.index("<")-1:]
                            claimed = discord.Embed(description=f"{case_num} has already been claimed by {previous_tech}",
                                        colour=discord.Color.yellow())
                            await interaction.response.send_message(embed=claimed, ephemeral=True,  delete_after=300)
                            return
                except:
                    pass

        #user has claimed the case successfully, add the new views.
        message_embed = discord.Embed(description=f"Is being worked on by <@{interaction.user.id}>",
                                colour=discord.Color.teal(),
                                timestamp=datetime.now())
        message_embed.set_author(name=f"{case_num}",                           icon_url=f'{interaction.user.display_avatar}')
        message_embed.set_footer(text="Claimed")
        await interaction.response.send_message(embed=message_embed, view=TechView(self.bot, interaction.user, case_num))
        return