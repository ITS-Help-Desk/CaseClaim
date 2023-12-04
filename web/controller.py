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
    """
    Use subprocess to start the bot and save it as a static private global var.
    """
    global _bot_process
    # Start the bot and capture all input and output
    if _bot_process != None:
        return "already running"
    _bot_process = subprocess.Popen(["python3", "main.py"], bufsize=8000,env=os.environ, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "running"

def stop_bot():
    """
    Send the bot an interrupt signal to kill it if it is running.
    """
    global _bot_process
    if _bot_process != None:
        # Terminate the bot process
        _bot_process.send_signal(signal.SIGINT)
        _bot_process = None
    return "not running"

def poll_bot():
    """
    Print information about bot exit or death.
    """
    global _bot_process
    if _bot_process != None:
        if _bot_process.poll():
            return f"Bot exited with code {_bot_process.returncode}"
        return "running"
    return "not running"

def get_buffered_outputs():
    """
    Grab the bots STDIN and STDERR and return it.

    @NOTE: Bugged I am not sure why but the communicate function does not work as expected.
    @TODO: Fix this bug and have it grab output in a reasonable amount of time (<1s) maybe asynchronously
    """
    global _bot_process
    if _bot_process != None:
        try:
            return _bot_process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            return ("","")
    return ("","")
        
