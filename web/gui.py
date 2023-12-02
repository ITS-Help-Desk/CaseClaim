from flask import Flask, Response, abort, request, render_template, redirect


import os
import mysql.connector
import base64

import web.controller as controller
from bot.models.checked_claim import CheckedClaim
import graphs.leadstats as leadstats_graphs
import graphs.casedist as casedist_graphs
import web.components as components
import datetime

token = None
connection = None
claims = None
app = Flask(__name__)
bot_running_status = "not running" # Migrate to boolean in controller.py at some point so the rendering in nav_col is easier


def load_token():
    global token
    token = os.environ.get("DISCORD_TOKEN")
    print(f"[FROM GUI]: Token = {token}")

def load_db_connector(connector: mysql.connector.MySQLConnection):
    global connection
    connection = connector

@app.route("/")
def default_page():
    global claims
    claims = CheckedClaim.search(connection)
    return render_template("index.html", 
                           nav_col=components.nav_column(components.SidebarOptions.DASHBOARD, 
                                                         bot_running_status != "not running", 
                                                         token != None), 
                           bot_controls=components.bot_controls(token == None))

@app.route("/stats/<graph>")
@app.route("/stats")
def stats_page(graph="leadstats"):
    global claims
    claims = CheckedClaim.search(connection)
    resource_path = ""
    match graph:
        case "leadstats":
            resource_path = "/leadstats.png"
        case "casedist":
            resource_path = "/casedist.png"
        case other:
            resource_path = "/leadstats.png"
    return render_template("stats.html",
                           nav_col=components.nav_column(components.SidebarOptions.STATISTICS,
                                                         bot_running_status != "not running",
                                                         token != None),
                           stats_box=components.stats_box(components.StatsType.IMAGE,
                                                          path=resource_path,
                                                          data="Lead statistics"
                                                          ),
                           graph_controls=components.stats_controls()
                           )


@app.route("/login")
def process_login():
    return "gaming"

@app.route("/leadstats.png")
def generate_leadstats_plot():
    png_data = leadstats_graphs.generate_leadstats_graph(claims, connection, datetime.datetime.now().isoformat())
    return Response(png_data.getvalue(), mimetype="image/png")

@app.route("/casedist.png")
def generate_casedist():
    cd_png_data = casedist_graphs.generate_casedist_plot(claims, datetime.datetime.now().month, datetime.datetime.now().day)
    return Response(cd_png_data.getvalue(), mimetype="image/png")


@app.post("/token")
def save_token():
    global token
    if token != None:
        abort(403)
    data = request.form
    if "token" not in data:
        abort(400)
    else: 
        with open("token.txt", "w") as token_file:
            token = data.getlist('token')[0]
            token_file.write(token)
            token_file.close()
    return redirect("/", code=302)

@app.route("/stop_bot")
def stop_bot():
    print("received stop bot")
    global bot_running_status
    bot_running_status = controller.stop_bot()
    print(controller.poll_bot())
    return redirect("/", code=302)

@app.route("/start_bot")
def start_bot():
    print("received start bot")
    global bot_running_status
    bot_running_status = controller.start_bot()
    print(controller.poll_bot())
    return redirect("/", code=302)





