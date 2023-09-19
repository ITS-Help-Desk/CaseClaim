import datetime
import io
import discord
import discord.ui as ui
import matplotlib.pyplot as plt

from bot.helpers import get_semester
from bot.helpers import month_number_to_name

from bot.models.checked_claim import CheckedClaim
from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.status import Status

if TYPE_CHECKING:
    from ..bot import Bot


class LeadStatsView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Month", style=discord.ButtonStyle.primary, custom_id="checkrefreshmonth")
    async def show_month(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the month.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        new_embed, file = await LeadStatsView.create_embed(self.bot, interaction)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])

    @ui.button(label="Semester", style=discord.ButtonStyle.primary, custom_id="checkrefreshsemester")
    async def show_semester(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the semester.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        new_embed, file = await LeadStatsView.create_embed(self.bot, interaction, month=False)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])

    @staticmethod
    async def create_embed(bot: 'Bot', interaction: discord.Interaction, month=True) -> list[discord.Embed, discord.File]:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): An instance of the Bot class.
            interaction_date (datetime.datetime): The time at which this request is made.
        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        m, s, mp, sp, mk, sk = LeadStatsView.get_data(bot, interaction.created_at)

        month_counts = m[0]
        month_keys = m[1]

        semester_counts = s[0]
        semester_keys = s[1]

        if month:
            counts = month_counts
            pings = mp
            kudos = mk
            keys = month_keys
        else:
            counts = semester_counts
            pings = sp
            kudos = sk
            keys = semester_keys

        labels = []
        data_points1 = []
        data_points2 = []
        data_points3 = []

        for key in keys:
            total = counts[key] + pings[key] + kudos[key]
            if total == 0:
                continue

            data_points1.append(counts[key])
            data_points2.append(pings[key])
            data_points3.append(kudos[key])

            user = User.from_id(bot.connection, key)
            labels.append(f"{user.abb_name} ({int((pings[key] / total) * 100)}% | {int((pings[key] / total) * 100)}%)")

        data_stream = LeadStatsView.convert_to_plot(f"ITS Lead CC Statistics ({f'{month_number_to_name(interaction.created_at.month)}' if month else 'Semester'})",
                                                    labels, data_points1, data_points2, data_points3)
        chart = discord.File(data_stream, filename="chart.png")

        embed = discord.Embed(title="ITS Case Check Leaderboard")
        embed.colour = bot.embed_color

        embed.set_image(
            url="attachment://chart.png"
        )

        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed, chart

    @staticmethod
    def convert_to_plot(title: str, labels: list[str], y1: list[int], y2: list[int], y3: list[int]) -> io.BytesIO:
        """Converts data into a plot that can be sent in a Discord message. It uses three
        parallel lists in order to generate the plot using matplotlib

        Args:
            title (str): The title of the graph
            labels (list[str]): The text labels for the bottom X axis of the graph
            y1 (list[int]): The data points for the checks
            y2 (list[int]): The data points for the pings

        Returns:
            io.BytesIO: The bytes that can be used to generate the graph
        """
        import pandas
        data_stream = io.BytesIO()
        users = []
        for i in range(len(y1)):
            user = []
            try:
                user.append(y1[i])
            except:
                pass
            try:
                user.append(y2[i])
            except:
                pass
            try:
                user.append(y3[i])
            except:
                pass

            users.append(user)

        df = pandas.DataFrame(users, index=labels)
        ax = df.plot.bar(stacked=True, title=title)
        ax.legend(["Checks", "Pings", "Kudos"])
        plt.xticks(rotation=45, ha="right")

        '''for p in ax.patches:
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy()
            ax.text(x + width / 2,
                    y + height + 0.1,
                    '{:.0f}%'.format(height),
                    horizontalalignment='center',
                    verticalalignment='center')'''
        #for p in ax.patches:
        #ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
        plt.close()
        data_stream.seek(0)

        return data_stream

    @staticmethod
    def get_data(bot: 'Bot', interaction_date: datetime.datetime) -> tuple[
        tuple[dict[int, int], list[int]], tuple[dict[int, int], list[int]], dict[int, int], dict[int, int], dict[int, int], dict[int, int]]:
        """Collects a large amount of data to be used by various commands and events within this bot.
        This function collects:
            - Total amount of cases claimed by each user by month
            - Total amount of cases claimed by each user by semester
            - Ranking of cases claimed by each user by month
            - Ranking of cases claimed by each user by semester
            - Total amount of pinged cases by each user by month
            - Total amount of pinged cases by each user by semester
        Args:
            bot (Bot): An instance of the bot class
            interaction_date (datetime.datetime): The time that this data was requested at.

        Returns:
            tuple[tuple[dict[int, int], list[int]], tuple[dict[int, int], list[int]], dict[int, int], dict[int, int]]:
            Returns the data in the format ((month counts, sorted month keys), (semester counts, sorted semester keys), month ping counts, semester ping counts, month kudos counts, semester kudos counts)
        """
        # Count the amount of cases worked on by each user
        month_counts = {}
        semester_counts = {}

        month_ping_counts = {}
        semester_ping_counts = {}

        month_kudos_counts = {}
        semester_kudos_counts = {}

        interaction_semester = get_semester(interaction_date)

        claims = CheckedClaim.search(bot.connection)
        for claim in claims:
            # Initialize information as zero
            month_counts.setdefault(claim.lead.discord_id, 0)
            semester_counts.setdefault(claim.lead.discord_id, 0)

            month_ping_counts.setdefault(claim.lead.discord_id, 0)
            semester_ping_counts.setdefault(claim.lead.discord_id, 0)

            month_kudos_counts.setdefault(claim.lead.discord_id, 0)
            semester_kudos_counts.setdefault(claim.lead.discord_id, 0)

            # Organize data for month
            if claim.claim_time.month == interaction_date.month:
                if claim.status == str(Status.CHECKED) or claim.status == str(Status.DONE):
                    month_counts[claim.lead.discord_id] += 1

                # Add pinged
                if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    month_ping_counts[claim.lead.discord_id] += 1

                # Add kudos
                if claim.status == Status.KUDOS:
                    month_kudos_counts[claim.lead.discord_id] += 1


            # Organize data for semester
            if get_semester(claim.claim_time) == interaction_semester:
                if claim.status == Status.CHECKED or claim.status == Status.DONE:
                    semester_counts[claim.lead.discord_id] += 1

                # Add pinged
                if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    semester_ping_counts[claim.lead.discord_id] += 1

                # Add kudos
                if claim.status == Status.KUDOS:
                    semester_kudos_counts[claim.lead.discord_id] += 1

        semester_counts_sorted_keys = sorted(semester_counts, key=semester_counts.get, reverse=True)
        month_counts_sorted_keys = sorted(month_counts, key=month_counts.get, reverse=True)

        return ((month_counts, month_counts_sorted_keys), (semester_counts, semester_counts_sorted_keys), month_ping_counts, semester_ping_counts, month_kudos_counts, semester_kudos_counts)
