#!/bin/bash

# Kill any running server processes
if ps aux | grep '[f]licd' &> /dev/null; then
    sudo kill $(ps aux | grep '[f]licd' | awk '{print $2}'); 
fi

# Kill any running client processes
if ps aux | grep '[l]ifxClient' &> /dev/null; then
    sudo kill $(ps aux | grep '[l]ifxClient' | awk '{print $2}');
fi

if ps aux | grep '[s]impleclient' &> /dev/null; then
    sudo kill $(ps aux | grep '[s]impleclient' | awk '{print $2}');
fi

# Need to sleep here before starting up the server process so it isn't killed by commands above
sleep 3

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

# Start up light control client
voltos use LIFXToken
voltos run "python3 clientlib/test_client.py"