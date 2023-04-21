#Import Statements
import discord
import discord.ui as ui
from discord import app_commands
from discord.ext import commands
import os
import csv
import random
from datetime import datetime

#Setting up the intents
intents = discord.Intents.default()
intents.message_content = True
#Variables
bot = commands.Bot(intents=discord.Intents.all(),
                   command_prefix="%",
                   case_insensitive=True,
                   strip_after_prefix=True)

#Gateway Event
@bot.event
async def on_ready():
  print(f"✅ {bot.user}")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

### INTERNAL COMMANDS ### 

#log_case writes the details of a concluded case from Discord into a csv file
def log_case(timestamp, casenum, status, lead, tech):
  time_string = str(timestamp)
  date_and_time = time_string.split(" ")
  truncated_time = date_and_time[1][:5]
  info = [[date_and_time[0], truncated_time, casenum, tech, status, lead]]
  with open(r"C:\Users\Helpdesk\Desktop\CaseClaimBot\log.csv", 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for element in info:
      writer.writerow(element)
  return

### OTHER COMMANDS ###

#mickie is a fun command
@bot.tree.command(name="mickie", description = "you're so fine,")
async def mickie(interaction: discord.Interaction):
  await interaction.response.send_message(f"Oh {interaction.user.mention} you're so fine, you blow my mind.")
  return

#help is a command for techs to utilise
@bot.tree.command(name="help", description = "Instructions for how to use the /claim command.")
async def help(interaction: discord.Interaction):
  await interaction.response.send_message("Claim a case using /claim followed by a case number.\n  - React with a ☑️ when you have completed the case.\n  - React with a ⚠️ to unclaim the case.\n", ephemeral = True, delete_after=300)
  return

def month_string_to_number(string):
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


#report is a command for lead techs to use to pull the log.csv file
@bot.tree.command(name="report",
                  description="Generate a report of cases logged.")
async def report(interaction: discord.Interaction,
                 user: discord.Member = None,
                 month: str = None):
  #check to see if user contains the @Lead role
  guild = interaction.user.guild
  lead_role = discord.utils.get(guild.roles, name="Lead")
  if lead_role in interaction.user.roles:
    try:
      #special case where the user asks for neither the user or the month
      if (user == None and month == None):
        print('case1')
        report_embed = discord.Embed(
          description=
          f"<@{interaction.user.id}>, here is the all-time, all-tech report!",
          color=discord.Color.teal())
        tech_report = discord.File(
          r"C:\Users\Helpdesk\Desktop\CaseClaimBot\log.csv")
        await interaction.response.send_message(embed=report_embed,
                                                file=tech_report)
        return

      #if the report asks for just the user
      if (user != None and month == None):
        print('case2')
        with open(r"C:\Users\Helpdesk\Desktop\CaseClaimBot\log.csv",
                  'r') as csvfile:
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
        month_num = month_string_to_number(month)
        with open(r"C:\Users\Helpdesk\Desktop\CaseClaimBot\log.csv",
                  'r') as csvfile:
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
        month_num = month_string_to_number(month)
        with open(r"C:\Users\Helpdesk\Desktop\CaseClaimBot\log.csv",
                  'r') as csvfile:
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
      with open(r"C:\Users\Helpdesk\Desktop\CaseClaimBot\temp.csv",
                'w',
                newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
          writer.writerow(row)

      tech_report = discord.File(
        r"C:\Users\Helpdesk\Desktop\CaseClaimBot\temp.csv")
      await interaction.response.send_message(embed=report_embed,
                                              file=tech_report)

    except:
      exception_embed = discord.Embed(
        description=
        f"<@{interaction.user.id}>, an error occured when trying to pull this report!",
        color=discord.Color.yellow())
      await interaction.response.send_message(embed=exception_embed,
                                              ephemeral=True)

  else:
    #return error message if user is not @Lead
    bad_user_embed = discord.Embed(
      description=
      f"<@{interaction.user.id}>, you do not have permission to pull this report!",
      color=discord.Color.yellow())
    await interaction.response.send_message(embed=bad_user_embed,
                                            ephemeral=True)


### PRIMARY COMMAND ###

class FeedbackModal(ui.Modal, title='Feedback Form'):
  def __init__(self, original_user, case_num):
    super().__init__()
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

    channel = interaction.user.guild.get_channel(1090066161980420148) #cases channel
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
    log_case(datetime.now(),self.case_num,f"Flagged, Reason: {self.description}",interaction.user.display_name,self.original_user.display_name)
    return

#Class for the Case-Claim Command's Lead Prompt View
class LeadView(discord.ui.View):
  def __init__(self, original_user, case_num):
    super().__init__(timeout=None)
    self.original_user = original_user #tech that claimed the case
    self.case_num = case_num
    
  @discord.ui.button(label="Check", style=discord.ButtonStyle.success)
  async def button_check(self, interaction, button):
    #Log the case as checked, then delete it
    log_case(datetime.now(),self.case_num,"Checked",interaction.user.display_name,self.original_user.display_name)
    
    await interaction.message.delete()
  
  @discord.ui.button(label="Flag", style=discord.ButtonStyle.danger)
  async def button_flag(self, interaction, button):
    #Prompt with Modal, record the response, create a private thread, then delete
    fbModal = FeedbackModal(self.original_user, self.case_num)
    await interaction.response.send_modal(fbModal)
    await interaction.message.delete()

#Class for the Case-Claim Command's Tech Prompt View
class TechView(discord.ui.View): 
  def __init__(self, original_user, case_num):
    super().__init__(timeout=None)
    self.original_user = original_user #tech that claimed the case
    self.case_num = case_num

  #if the user is the same as the claimer, 
  @discord.ui.button(label="Complete", style=discord.ButtonStyle.success)
  async def button_claim(self, interaction, button):
    if(self.original_user == interaction.user):
      channel = interaction.user.guild.get_channel(1088650338652913695) #claims channel
      if random.random() < 1:   #percentage of cases sent to claims
        #send a message in the claims channel and add the lead view to it.
          lead_embed = discord.Embed(description=f"Has been marked as complete by <@{self.original_user.id}>",
                        colour=discord.Color.teal(),
                        timestamp=datetime.now())
          lead_embed.set_author(name=f"{self.case_num}",icon_url=f'{self.original_user.display_avatar}')
          lead_embed.set_footer(text="Completed")
          await channel.send(embed=lead_embed, view=LeadView(self.original_user,self.case_num))
      log_case(datetime.now(),self.case_num,"Complete","Bot",self.original_user.display_name)
      await interaction.message.delete()

      completed_embed = discord.Embed(description=f"Has been marked complete by <@{self.original_user.id}>",
                        colour=discord.Color.green(),
                        timestamp=datetime.now())
      completed_embed.set_author(name=f"{self.case_num}",icon_url=f'{self.original_user.display_avatar}')
      completed_embed.set_footer(text="Completed")
      channel2 = interaction.user.guild.get_channel(1090066161980420148) #cases channel
      await interaction.response.send_message(embed=completed_embed, ephemeral=True)
      
    else:
      not_yours = discord.Embed(description=f"{interaction.user}, you didn't claim this case!",
        colour=discord.Color.yellow())
      await interaction.response.send_message(embed=not_yours, ephemeral=True, delete_after=300)
      
  #if the user is the same as the claimer or is a lead, then deletes, else responds with error
  @discord.ui.button(label="Unclaim", style=discord.ButtonStyle.secondary)
  async def button_unclaim(self, interaction, button):
    guild = interaction.message.guild
    lead_role = discord.utils.get(guild.roles, name="Lead")
    if(self.original_user == interaction.user or lead_role in interaction.user.roles):
      await interaction.message.delete()
    else:
      not_yours = discord.Embed(description=f"{interaction.user}, you didn't claim this case!",
        colour=discord.Color.yellow())
      await interaction.response.send_message(embed=not_yours, ephemeral=True, delete_after=300)
      return
    
#Case-Claim Command
@bot.tree.command(name="claim", description = "Claim cases using this command.")
@app_commands.describe(case_num="Case #")
async def claim(interaction: discord.Interaction, case_num: str):
  #defining the cases channel and the claims channel
  channel = interaction.user.guild.get_channel(1090066161980420148) #cases channel

  #check to see if the number entered is an 8 digit number
  if not case_num.isdigit() or len(case_num) != 8:
    invalid = discord.Embed(description=f"{case_num} is an invalid case number!",
                        colour=discord.Color.yellow())
    await interaction.response.send_message(embed=invalid, ephemeral=True, delete_after=300)
    return

  #check to see if the case claimed has already been claimed and is in progress.
  async for message in channel.history(limit=50):
    if message.author == bot.user: #checks to see if the bot sent the message
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
  await interaction.response.send_message(embed=message_embed, view=TechView(interaction.user, case_num))
  return

bot.run("MTA3NjI5MjU4MjYyMTA1NzA5NA.G9w6zs.k5g06fabboAC3DEaU4qT7AlTSEIUglUUq3V3g4")
