from flask import Flask, Response, abort, request, render_template, redirect, session

import secrets
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
app = Flask(__name__)
bot_running_status = "not running" # Migrate to boolean in controller.py at some point so the rendering in nav_col is easier
app.secret_key = secrets.token_hex(32)
password = "CHANGE_ME_IN_PROD"


def load_token():
    """
    Read the bot token from the environment. This method is used by the server startup script.
    """
    global token
    token = os.environ.get("DISCORD_TOKEN")
    print(f"[FROM GUI]: Token = {token}")

def load_db_connector(connector: mysql.connector.MySQLConnection):
    """
    Save a DB connector to the case claim DB.
    """
    global connection
    connection = connector



@app.route("/")
def default_page():
    """
    Render index.html based on the current bot state.
    """
    if "username" not in session:
        return redirect("/login")
    return render_template("index.html", 
                           nav_col=components.nav_column(components.SidebarOptions.DASHBOARD, 
                                                         bot_running_status != "not running", 
                                                         token != None), 
                           bot_controls=components.bot_controls(token == None),
                           login_controls=components.login_controls(True)
                           )

@app.route("/stats/<graph>/<time>")
@app.route("/stats/<graph>")
@app.route("/stats")
def stats_page(graph="leadstats", time="month"):
    """
    Render the statistics page based on requested stat and current bot state.

    @NOTE: Using claims as a global because performing too many queries with the same connector
           errors the db connection out.

    Args:
        graph   The graph requested
        time    The time frame to generate the graph on
    """
    resource_path = ""
    match graph:
        case "leadstats":
            resource_path = f"/leadstats/{time}"
        case "casedist":
            resource_path = "/casedist"
        case other:
            resource_path = "/leadstats/month"
    if "username" in session:
        return render_template("stats.html",
                               nav_col=components.nav_column(components.SidebarOptions.STATISTICS,
                                                             bot_running_status != "not running",
                                                             token != None),
                               stats_box=components.stats_box(components.StatsType.IMAGE,
                                                              path=resource_path,
                                                              data="Lead statistics"),
                               graph_controls=components.stats_controls(),
                               login_controls=components.login_controls(True))
    else:
        return redirect("/login")


@app.route("/login", methods=['GET', 'POST'])
def process_login():
    """
    Use flask session to auth users
    """
    if request.method == 'POST':
        if "password" in request.form and request.form["password"] == password:
            session['username'] = "auth"
            return redirect("/")
        else:
            return render_template("login.html", 
                            incorrect_flag=components.alert("Incorrect Password", "danger"))
    return render_template("login.html")
    
@app.route("/logout")
def process_logout():
    """
    Sign the current user out if they are logged in
    """
    if "username" in session:
        session.pop('username', None)
    return redirect("/")

@app.route("/leadstats/<time>")
def generate_leadstats_plot(time):
    """
    Generate the leadstats graph based on the requested time

    Args:
        time    A string representing a month or a semester.
    """
    if "username" not in session:
        abort(401)
    claims = CheckedClaim.search(connection)
    png_data = leadstats_graphs.generate_leadstats_graph(claims,connection, time != "semester", datetime.datetime.now().isoformat())
    return Response(png_data.getvalue(), mimetype="image/png")

@app.route("/casedist")
def generate_casedist():
    """
    Generate a case distribution graph covering the prior 24 hours.

    @TODO: Implement form to allow arbitrary timeframes
    """
    if "username" not in session:
        abort(401)
    claims = CheckedClaim.search(connection)
    cd_png_data = casedist_graphs.generate_casedist_plot(claims, datetime.datetime.now().month, datetime.datetime.now().day)
    return Response(cd_png_data.getvalue(), mimetype="image/png")


@app.post("/token")
def save_token():
    """
    Save a token entered by the user on the website.
    """
    global token
    if token != None:
        abort(403)
    data = request.form
    if "token" not in data:
        abort(400)
    if "username" not in session:
        abort(401)
    else: 
        with open("token.txt", "w") as token_file:
            token = data.getlist('token')[0]
            token_file.write(token)
            token_file.close()
    return redirect("/", code=302)

@app.route("/stop_bot")
def stop_bot():
    """
    Use controller to stop bot.
    """
    if "username" not in session:
        abort(401)
    print("received stop bot")
    global bot_running_status
    bot_running_status = controller.stop_bot()
    print(controller.poll_bot())
    return redirect("/", code=302)

@app.route("/start_bot")
def start_bot():
    """
    Use controller to start the bot
    """
    if "username" not in session:
        abort(401)
    print("received start bot")
    global bot_running_status
    bot_running_status = controller.start_bot()
    print(controller.poll_bot())
    return redirect("/", code=302)





