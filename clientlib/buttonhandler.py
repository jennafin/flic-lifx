import sys
import fliclib
#import config_file_parser
from enum import Enum

class ConfigButtonHandler(object):
    """Listens for button clicks and prints out the button address whenever a button is clicked. This is to facilitate writing a config file to map button presses to light actions.
    """
    
    def __init__(self):
        """Inits ConfigButtonHandler by starting up a FlicClient to listen for button presses.
        """
        self.client = fliclib.FlicClient("localhost")
        
    def _on_button_single_or_double_click_or_hold(self, channel, click_type, was_queued, time_diff):
        """Function to execute whenever a connected button is pressed. Prints out the button address.
    
        Args:
            channel: the button channel the click event occurred on.
            click_type: the click type that occurred.
            was_queued: bool indicating whether this was a queued click event.
            time_diff: ???
        """
        # Don't care about queued presses
        if not was_queued:
            print("Button pressed: " + channel.bd_addr)
        
    def _got_button(self, bd_addr):
        """Creates a button connection channel and assigns the handler function for button presses for a particular button.
    
        Args:
            bd_addr: button address.
        """
        cc = fliclib.ButtonConnectionChannel(bd_addr)
        cc.on_button_single_or_double_click_or_hold = self._on_button_single_or_double_click_or_hold
        self.client.add_connection_channel(cc)
        
    def _got_info(self, items):
        """Handler for getting info from the button server. Calls got_button for each button address it receives from the server.
    
        Args:
            items: information retrieved from the server. We only care about the button addresses of verified buttons.
        """
        for bd_addr in items["bd_addr_of_verified_buttons"]:
            self._got_button(bd_addr)
        
    def start(self):     
        """Initializes the ButtonConnectionChannels and starts listening for button events.
        """       
        # Get button information
        self.client.get_info(self._got_info)
        self.client.on_new_verified_button = self._got_button
        
        # Handle button events
        print("\n**********   Running in config mode   **********")
        print("Client is now listening for button events. Press a Flic button to display its address")
        self.client.handle_events()
        
        
class ButtonHandler(object):
    """Handles button presses by calling the appropriate function for the button action that occurred.
    """
    
    class SectionType(Enum):
        Action = 'ACTION'
        Button = 'BUTTON'
        State = 'STATE'
    
    def __init__(self):
        """Inits ButtonHandler by starting up a FlicClient to listen for button presses. Also creates a dictionary mapping click types to functions to handle them.
        """
        self.client = fliclib.FlicClient("localhost")
        self.click_functions = {
            'ClickType.ButtonSingleClick': self._on_single_click,
            'ClickType.ButtonDoubleClick': self._on_double_click,
            'ClickType.ButtonHold': self._on_hold
        }
        self.buttons = {}
        self.actions = {}
        self.states = {}
        
        self.light_service = None
    
    def _on_connection_status_changed(self, channel, connection_status, disconnect_reason):
        """Function that is called whenever a buttons connection status is changed.
        
        Args:
            channel: button channel that had a connection status change.
            connection_status: the current connection_status.
            disconnect_reason: the reason why the connection was disconnected (if it was disconnected).
        """
        pass
        
    def _on_button_single_or_double_click_or_hold(self, channel, click_type, was_queued, time_diff):
        """Function to execute whenever a connected button is pressed. Executes the appropriate click_type handler function.
    
        Args:
            channel: the button channel the click event occurred on.
            click_type: the click type that occurred.
            was_queued: bool indicating whether this was a queued click event.
            time_diff: ???
        """
        # Execute the appropriate click function with the button address as the argument
        if not was_queued:
            #self.click_functions[str(click_type)](channel.bd_addr)
            print("Button click!")

    def _on_single_click(self, button_addr):
        """Function to handle single clicks for a certain button.
        
        Args:
            button_addr: address of the button that was clicked.
        """
        button_action_name = self.buttons[button_addr].single_click_action
        button_action = self.actions[button_action_name]
        self._do_button_action(button_action)
            
    def _on_double_click(self, button_addr):
        """Function to handle double clicks for a certain button.
        
        Args:
            button_addr: address of the button that was clicked.
        """
        button_action_name = self.buttons[button_addr].double_click_action
        button_action = self.actions[button_action_name]
        self._do_button_action(button_action)
        
    def _on_hold(self, button_addr):
        """Function to handle a button hold for a certain button.
        
        Args:
            button_addr: address of the button that was clicked.
        """
        button_action_name = self.buttons[button_addr].hold_action
        button_action = self.actions[button_action_name]
        self._do_button_action(button_action)
            
    def _do_button_action(self, button_action):
        if button_action.action_type == 'Toggle':
            self.light_service.toggle(button_action.selector, button_action.duration)
        elif button_action.action_type == 'ActivateScene':
            self.light_service.activate_scene(button_action.uuid, button_action.duration)
        elif button_action.action_type == 'SetState':
            state = self.states[button_action.state]
            self.light_service.set_state(state, button_action.selector)
        elif button_action.action_type == 'SetStates':
            states = []
            for state_name in button_action.states:
                states.append(self.states[state_name])
            self.light_service.set_states(states, self.states[button_action.default])
        
    def _got_button(self, bd_addr):
        """Creates a button connection channel and assigns the handler function for button presses for a particular button.
    
        Args:
            bd_addr: button address.
        """
        cc = fliclib.ButtonConnectionChannel(bd_addr)
        #cc.on_connection_status_changed = self._on_connection_status_changed
        cc.on_button_single_or_double_click_or_hold = self._on_button_single_or_double_click_or_hold
        self.client.add_connection_channel(cc)
        
    def _got_info(self, items):
        """Handler for getting info from the button server. Calls _got_button for each button address it receives from the server.
    
        Args:
            items: information retrieved from the server. We only care about the button addresses of verified buttons.
        """
        for bd_addr in items["bd_addr_of_verified_buttons"]:
            self._got_button(bd_addr)
    
    def _load_config(self, light_service):
        """Loads the button config from the config file. Essentially maps button click types to light actions.
        """
        config = config_file_parser.ConfigFileParser()
        config_data = config.get_config()
        self.buttons = config_data['buttons']
        self.actions = config_data['actions']
        self.states = config_data['states']
        
    def start(self, light_service):
        """Loads the button config, initializes the ButtonConnectionChannels, and starts listening for button events.
        """
        
        self.light_service = light_service
        #self._load_config(light_service)
            
        # Get button information
        self.client.get_info(self._got_info)
        self.client.on_new_verified_button = self._got_button
        
        # Handle button events
        print("\nClient is now listening for button events. Press a Flic button to test it out!")
        #self.client.handle_events()


    
