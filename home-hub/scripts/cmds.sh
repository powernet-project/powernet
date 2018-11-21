#!/bin/bash

cd ~/

echo "Writing aliases to your .bashrc file..."
echo alias gohh="'cd HomeHub/home-hub/'" >> .bashrc
echo alias ll="'ls -la'" >> .bashrc
echo alias gs="'git status'" >> .bashrc
echo alias gpr="'git pull --rebase'" >> .bashrc
echo alias killpython="'ps -a | grep python | awk \"{print $0}\" | xargs kill -9'" >> .bashrc
echo "Done writing aliases to your .bashrc file. Reloading your source..."
echo "Write google credentials directory"
echo export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/GCP_pubsub/pwrnet-80eaae3af223.json" >> .bashrc
source ~/.bashrc
