from flask import Flask, abort, request, render_template

app = Flask(__name__)
token = "mytoken"
bot_running_status = "running"


@app.route("/", methods=['GET'])
def default_page():
    return render_template("index.html", stylesheet="", token=token, bot_running_status=bot_running_status)

@app.get("/login")
def render_login():
    return ":) todo later"

@app.post("/login")
def process_login():
    return "gaming"

@app.route("/token", methods=["POST"])
def save_token():
    data = request.form

    if "token" not in data:
        abort(400)
    else:
        with open("../token.txt", "w") as token_file:
            token_file.write(data["token"])
            token_file.close()
    return "Token Received"

@app.route("/stop_bot")
def stop_bot():
    return "<p>Stopping bot</p>"

@app.route("/start_bot")
def start_bot():
    return "<p>start bot</p>"





