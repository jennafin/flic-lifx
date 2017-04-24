#!/bin/bash

# Kill any running server or client processes
found_server=$(ps aux | grep '[f]licd')
found_client=$(ps aux | grep '[c]lientlib/client.py')

if [ "$found_server" ]; then
    sudo kill $(ps aux | grep '[f]licd' | awk '{print $2}'); 
fi

if [ "$found_client" ]; then
    sudo kill $(ps aux | grep '[c]lientlib/client.py' | awk '{print $2}');
fi

# Need to sleep here before starting up the server process so it isn't killed by commands above
sleep 3
echo "sleep"

# Start server in separate terminal - supports ubuntu for testing purposes
if [[ $(arch) == "x86_64" ]]; then
     pushd bin/x86_64 &> /dev/null
     gnome-terminal -e 'sudo ./flicd -f flic.sqlite3'
     popd &> /dev/null
elif [[ $(arch) == "armv7l" ]]; then
     pushd bin/armv6l &> /dev/null
     lxterminal -e 'sudo ./flicd -f flic.sqlite3'
     popd &> /dev/null
else
    echo "Unsupported OS"
    exit
fi

echo "The server has been launched in another terminal."
echo "It may require your credentials, please check..."
echo

# Wait 15 seconds so user can enter credentials - spin from http://stackoverflow.com/questions/12498304/using-bash-to-display-a-progress-working-indicator
spin='-\|/'
j="0"
while [ $j -lt 150 ]
do
  i=$(( (i+1) %4 ))
  printf "\r${spin:$i:1}"
  sleep .1
  j=$[$j+1]
done

python3 clientlib/new_scan_wizard.py