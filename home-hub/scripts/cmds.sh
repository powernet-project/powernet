#!/bin/bash

cd ~/

echo "Writing aliases to your .bashrc file..."
echo alias gohh="'cd HomeHub/home-hub/'" >> .bashrc
echo alias ll="'ls -la'" >> .bashrc
echo alias gs="'git status'" >> .bashrc
echo alias gpr="'git pull --rebase'" >> .bashrc
echo "Done writing aliases to your .bashrc file. Reloading your source..."
source ~/.bashrc
