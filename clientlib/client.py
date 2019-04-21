#!/usr/bin/env python3

#import lightservice
import buttonhandler
import sys
import argparse

from lifxlan import LifxLAN

def main():
    """Main client for listening to button presses and executing the correct handlers to do light events. 
    """
    # Parse arguments for configuration and light type
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config_mode", action='store_true', help="runs the client in config mode which prints out the light data")
    
    args = parser.parse_args()
    config_mode = args.config_mode
    
    lifx = LifxLAN(None)

    devices = lifx.get_devices()
    device = lifx.get_devices_by_group("Bedroom")
    #print(device.get_device_list()[0])
    
    button_handler = None
    if config_mode:
        button_handler = buttonhandler.ConfigButtonHandler()
        button_handler.start()
    else:
        button_handler = buttonhandler.ButtonHandler()
        button_handler.start(lifx)
    

if __name__ == "__main__":
    main()
