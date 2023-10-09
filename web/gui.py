from flask import Flask, abort, request, render_template, redirect
import os
import web.controller as controller

token = None
app = Flask(__name__)
bot_running_status = "not running"

def load_token():
    global token
    token = os.environ.get("DISCORD_TOKEN")
    print(f"[FROM GUI]: Token = {token}")


@app.route("/", methods=['GET'])
def default_page():
    return render_template("index.html", stylesheet="", token=token, bot_running_status=bot_running_status, console_output="")

@app.route("/login")
def process_login():
    return "gaming"

@app.post("/token")
def save_token():
    global token
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





