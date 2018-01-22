"""Main application for flic-lifx
"""
# pylint: disable=wrong-import-position
import logging
import sys
import threading
sys.path.append('../')
from clientlib import fliclib
from clientlib.button import Button
from flask import Flask, render_template
#from wtforms import (Form, StringField, SubmitField, TextAreaField, TextField,
#                     validators)

# Web app config
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

class FlicLifxApp(object):
    """Main application for flic-lifx
    """

    def __init__(self):
        self.client = fliclib.FlicClient("localhost")
        self.buttons = []
        self.waiter = threading.Event()

    def got_button(self, bd_addr):
        """Defines the action to take when we discover a button
        """
        # Create the connection channel for the button
        connection_channel = fliclib.ButtonConnectionChannel(bd_addr)

        # Set the 'on button up or down' action
        connection_channel.on_button_up_or_down = \
            lambda channel, click_type, was_queued, time_diff: \
                logging.info(channel.bd_addr + " " + str(click_type))

        # Set the on connection status changed action
        connection_channel.on_connection_status_changed = \
            lambda channel, connection_status, disconnect_reason: \
                logging.info(channel.bd_addr \
                + " " + str(connection_status) \
                + (" " + str(disconnect_reason) \
                if connection_status == fliclib.ConnectionStatus.Disconnected else ""))

        # Add the connection channel to the client object
        self.client.add_connection_channel(connection_channel)

        # Add the button to the list of buttons we're tracking
        self.buttons.append(Button(bd_addr))

    def got_info(self, items):
        """Defines the action to take when we receive the info from get_info call
        """
        for bd_addr in items["bd_addr_of_verified_buttons"]:
            self.got_button(bd_addr)
        self.waiter.set() # We now have button info

    def hello(self):
        """Gets button info from flic client, sets action to take
        for a newly verified button, and starts the main client loop.
        """
        self.client.get_info(self.got_info)
        self.client.on_new_verified_button = self.got_button

        # Start main button listener thread
        threading.Thread(target=self.client.handle_events).start()

        # Waits for got_info() to be called, then logs the info
        self.waiter.wait()
        for i in self.buttons:
            logging.info(i)

        # Start main HTTP app server
        app.run(host='0.0.0.0', use_reloader=False)

@app.route("/", methods=['GET', 'POST'])
def start():
    """Starts the main http web app
    """
    return render_template('main.html')

if __name__ == "__main__":
    logging.basicConfig(filename='flic-lifx.log', filemode='w', level=logging.DEBUG)
    MAIN_APPLICATION = FlicLifxApp()
    MAIN_APPLICATION.hello()
