import tkinter as tk
import multiprocessing
from types import FunctionType

class BotGui:
    def __init__(self, bot_main: FunctionType):
        """ 
        Setup all widgets and frames for simple GUI using tkinter and using multiprocessing as a wrapper
        to control the bot process.

        """

        # Setup the window
        self.window = tk.Tk()
        self.window.title("Case Claim Bot")
        
        # Save the bot main function so we can restart it later
        self.bot_main = bot_main

        self.__init_constants()
        self.__create_frames()
        
        # Create the bot process by calling the bot's main method with no cmd line args and start it
        self.bot_process = multiprocessing.Process(target=self.bot_main,args=())
        self.bot_process.start()
        
        self.__create_widgets()

        # Start the window main loop
        self.window.mainloop()

        # Wait for the child bot process to terminate before ending this program.
        self.bot_process.join()
    
    def __init_constants(self):
        """
        Initialize constants important for tkinter parameters so they are easy to modify later.
        """
        self.BUTTON_FRAME_PARENT = self.window
        self.BUTTON_FRAME_WIDTH = 200
        self.BUTTON_FRAME_HEIGHT = 200

        self.STATUS_FRAME_PARENT = self.window
        self.STATUS_FRAME_WIDTH = 200
        self.STATUS_FRAME_HEIGHT = 200

        self.OUTPUT_FRAME_PARENT = self.window
        self.OUTPUT_FRAME_HEIGHT = 200
        self.OUTPUT_FRAME_WIDTH = 200



    def __create_frames(self):
        """
        Create all frames for the gui and grid them in the window according to the predetermined constants.
        """
        self.buttons_frame = tk.Frame(self.BUTTON_FRAME_PARENT, borderwidth=1, relief="solid", width=self.BUTTON_FRAME_WIDTH, height=self.BUTTON_FRAME_HEIGHT)
        self.buttons_frame.grid(row=1,column=1)

        self.status_frame = tk.Frame(self.STATUS_FRAME_PARENT, borderwidth=1, relief="solid", width=self.STATUS_FRAME_WIDTH, height=self.STATUS_FRAME_HEIGHT)
        self.status_frame.grid(row=1, column=3)
        
        self.output_frame = tk.Frame(self.OUTPUT_FRAME_PARENT, borderwidth=1, relief="solid", width=self.OUTPUT_FRAME_WIDTH, height=self.OUTPUT_FRAME_HEIGHT)
        self.output_frame.grid(row=1,column=2)

    def __create_widgets(self):
        """
        Create all widgets/viewable elements for the gui and grid them in their parent frames.
        """

        # Create the start bot button and attach self.start_bot as the function to execute on a click
        self.start_bot_button = tk.Button(self.buttons_frame, text="Start Bot", command=self.start_bot)
        self.start_bot_button.grid(row=1, column=1)

        # Create the stop bot button and attach self.stop_bot as the function to execute on a click
        self.stop_bot_button = tk.Button(self.buttons_frame, text="Stop Bot", command=self.stop_bot)
        self.stop_bot_button.grid(row=2, column=1)

        # Create exit button that calls quit on click
        self.exit_button = tk.Button(self.buttons_frame, text="Exit", command=self.quit)
        self.exit_button.grid(row=3, column=1)

        # Create a radiobutton that serves to indicate if the bot is running or not.
        # NOTE: If the bot is killed with .terminate() or .kill() it is not reflected in discord until the gui is closed.
        # TODO: Change radiobuttons to colored boxes to avoid the disabled lines; Export to a ButtonsFrame class.
        self.bot_is_running_var = tk.StringVar()
        self.bot_is_running_box = tk.Radiobutton(self.status_frame, text="Bot is Running", variable=self.bot_is_running_var, value="1")
        self.bot_is_running_box["state"] = 'disabled' # prevent user from changing the button
        self.bot_is_running_box.grid(row=1,column=1)
        self.bot_is_running_var.set("1") # On by default since the bot is started on initialization
        
        self.bot_token_found_var = tk.StringVar()
        self.bot_token_found_box = tk.Radiobutton(self.status_frame, text="Bot Token Found", variable=self.bot_token_found_var, value="1")
        self.bot_token_found_box.grid(row=2,column=1)
        self.bot_token_found_box['state'] = 'disabled'
        self.bot_token_found_var.set("0") # Off by default


    def start_bot(self):
        """
        Start a new bot process if the previous one is dead or has been terminated.
        """

        # Do nothing if the bot is still running, else free the process resources and hard kill it and restart the bot.
        if self.bot_process.is_alive():
            pass
        else:
            self.stop_bot()
            self.bot_process.close()
            self.bot_process = multiprocessing.Process(target=self.bot_main, args=())
            self.bot_process.start()
            self.bot_is_running_var.set("1")


    def stop_bot(self):
        """
        Stop the bot if it is still running by sending it a SIGKILL (UNIX) or using Windows TerminateProcess() call.
        """
        if self.bot_process.is_alive() or self.bot_process.exitcode != None:
            self.bot_is_running_var.set("0")
            self.bot_process.kill()
            self.bot_process.join() # Wait for bot to fully die before continuing

    def quit(self):
        """
        Stop the bot and destroy the gui.
        """
        self.stop_bot()
        self.window.destroy()


if __name__ == "__main__":
    print("Run my driver in the root of the project: python3 run_gui.py")

