import datetime
import time
import io
from mysql.connector import MySQLConnection
import matplotlib.pyplot as plt
from bot.models.checked_claim import CheckedClaim
from matplotlib import ticker

def generate_casedist_plot(claims: list[CheckedClaim], month: int, day: int):
    current = datetime.datetime.now()
    start = datetime.datetime(year=current.year, month=month, day=day, hour=7, minute=0, second=0)

    days = []  # 44 segments
    for i in range(44):
        days.append(0)

    # Generate data
    for claim in claims:
        if claim.claim_time > start:
            start_time = claim.claim_time.replace(hour=7, minute=0, second=0)
            fixed_date = int(time.mktime(claim.claim_time.timetuple())) - int(time.mktime(start_time.timetuple()))

            index = (fixed_date // 60) // 15

            days[min(index, len(days) - 1)] += 1

    # Create graph
    data_stream = io.BytesIO()
    plt.switch_backend('Agg')
    fig, ax = plt.subplots()

    labels = create_labels()

    # Create plot
    ax.set_title(f"Total Case Claim-Time Histogram (Starting {start.strftime('%b %d, %Y')})")
    plt.xticks(rotation=90, ha="right")

    ax.bar(labels, days, color="b", zorder=3)

    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=13))

    # Save as stream
    fig.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
    plt.close()
    data_stream.seek(0)
    return data_stream

def create_labels() -> list[str]:
    """
    Creates a list of labels for the graph broken up by 15 minute increments
        7:00, 7:15, 7:30, 7:45, 8:00...

    Returns:
        list[str]: A list with all labels
    """
    labels = []

    hour = 7
    minute = 0
    for i in range(44):
        next_minute = minute + 15
        next_hour = hour
        if next_minute >= 60:
            next_minute = 0
            next_hour += 1
            if next_hour > 12:
                next_hour %= 12

        fminute = f"0{minute}" if minute < 10 else str(minute)
        labels.append(f"{hour}:{fminute}")

        minute = next_minute
        hour = next_hour

    return labels
