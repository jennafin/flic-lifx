#!/bin/bash

found_server=$(ps aux | grep '[f]licd')
found_client=$(ps aux | grep '[c]lientlib/client.py')

# If the client or server is not running, run the start script.
if [[ -z "$found_server" ]] || [[ -z "$found_client" ]]; then  
    lxterminal --command "/home/pi/Documents/flic-lifx/start.sh"
fi