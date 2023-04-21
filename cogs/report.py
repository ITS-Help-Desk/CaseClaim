from discord import app_commands
from discord.ext import commands
import discord
import csv
import os


class Report(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        
        if '/' in self.bot.file_path:
            self.temp_file_path = f"{self.bot.file_path}/temp.csv"
        else:
            self.temp_file_path = f"{self.bot.file_path}/temp.csv"
    

    @app_commands.command(description = "Generate a report of cases logged.")
    async def report(self, interaction: discord.Interaction, user: discord.Member = None, month: str = None):
        #check to see if user contains the @Lead role
        guild = interaction.user.guild
        lead_role = discord.utils.get(guild.roles, name="Lead")
        #if lead_role in interaction.user.roles:
        if True:
            try:
                #special case where the user asks for neither the user or the month
                if (user == None and month == None):
                    print('case1')
                    report_embed = discord.Embed(
                    description=
                    f"<@{interaction.user.id}>, here is the all-time, all-tech report!",
                    color=discord.Color.teal())
                    tech_report = discord.File(self.bot.log_file_path)
                    await interaction.response.send_message(embed=report_embed, file=tech_report)
                    return

                #if the report asks for just the user
                if (user != None and month == None):
                    print('case2')
                    with open(self.bot.log_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        rows = []
                        for row in reader:
                            if row[3] == f'{user.display_name}':
                                rows.append(row)

                    report_embed = discord.Embed(
                    description=
                    f"<@{interaction.user.id}>, here is the report for <@{user.id}>",
                    color=discord.Color.teal())

                #if the report asks for only the month
                if (user == None and month != None):
                    print('case3')
                    month_num = self.month_string_to_number(month)
                    with open(self.bot.log_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        rows = []
                        for row in reader:
                            if row[0][5:7] == month_num:
                                rows.append(row)

                    report_embed = discord.Embed(
                    description=
                    f"<@{interaction.user.id}>, here is the report for the month of {month}",
                    color=discord.Color.teal())

                #if the report command asks for both!
                if (user != None and month != None):
                    print('case4')
                    month_num = self.month_string_to_number(month)
                    with open(self.bot.log_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                    rows = []
                    for row in reader:
                        if row[0][5:7] == month_num and row[3] == f'{user.display_name}':
                            rows.append(row)
                    report_embed = discord.Embed(
                    description=
                    f"<@{interaction.user.id}>, here is the report for <@{user.id}> for the month of {month}",
                    color=discord.Color.teal())

                #generates and returns the requested file
                with open(self.temp_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for row in rows:
                        writer.writerow(row)

                tech_report = discord.File(self.temp_file_path)
                await interaction.response.send_message(embed=report_embed, file=tech_report)
            except:
                exception_embed = discord.Embed(
                    description=
                    f"<@{interaction.user.id}>, an error occured when trying to pull this report!",
                    color=discord.Color.yellow())
                await interaction.response.send_message(embed=exception_embed, ephemeral=True)

        else:
            #return error message if user is not @Lead
            bad_user_embed = discord.Embed(
            description=
            f"<@{interaction.user.id}>, you do not have permission to pull this report!",
            color=discord.Color.yellow())
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True)

    def month_string_to_number(self, string):
        m = {
            'jan': '01',
            'feb': '02',
            'mar': '03',
            'apr': '04',
            'may': '05',
            'jun': '06',
            'jul': '07',
            'aug': '08',
            'sep': '09',
            'oct': '10',
            'nov': '11',
            'dec': '12'
        }
        s = string.strip()[:3].lower()
        try:
            out = m[s]
            return out
        except:
            raise ValueError('Not a month')