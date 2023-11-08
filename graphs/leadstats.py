import io
import mysql

# Not ideal but better than a full rewrite right now
from bot.models.checked_claim import CheckedClaim
from bot.helpers.leaderboard_helpers import LeadstatsResults

from mysql.connector import MySQLConnection
from datetime import datetime

def generate_leadstats_graph(connection: MySQLConnection, date: str) -> io.BytesIO:
    claims = CheckedClaim.search(connection)
    results = LeadstatsResults(claims, datetime.fromisoformat(date))

    # Force only current month mode. In the future give choice between semester and month
    data_stream = results.convert_to_plot(connection, True, "ITS Lead CC Statistics for Current Month")
    return data_stream 
    

