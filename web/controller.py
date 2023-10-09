import subprocess
import os
import signal

"""
NOTE: 

Only have one tab open for this at any time. Currently this controller is not multiprocessing safe.
If multiple people have tabs open in a server that uses multiple threads to serve as client workers
it will mess up the bot because each one will try to use the same token.

"""

_bot_process: subprocess.Popen | None = None

def start_bot():
    global _bot_process
    # Start the bot and capture all input and output
    if _bot_process != None:
        return "already running"
    _bot_process = subprocess.Popen(["python3", "main.py"], bufsize=8000,env=os.environ, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "running"

def stop_bot():
    global _bot_process
    if _bot_process != None:
        # Terminate the bot process
        _bot_process.send_signal(signal.SIGINT)
        _bot_process = None
    return "not running"

def poll_bot():
    global _bot_process
    if _bot_process != None:
        if _bot_process.poll():
            return f"Bot exited with code {_bot_process.returncode}"
        return "running"
    return "not running"

def get_buffered_outputs():
    global _bot_process
    if _bot_process != None:
        try:
            return _bot_process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            return ("","")
    return ("","")
        
