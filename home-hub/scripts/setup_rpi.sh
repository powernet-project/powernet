#!/bin/bash

cd ~/
echo "Creating project directory..."
mkdir HomeHub
cd HomeHub
echo "Initializing the Git repo..."
git init
git config core.sparsecheckout true # allows us to checkout only a portion of the repo
echo home-hub/ >> .git/info/sparse-checkout # defines which part of the repo we want to check out
echo "Adding the Powernet remote (repo)"
git remote add -f origin https://github.com/powernet-project/powernet.git
echo "Pulling the latest from master"
git pull origin master
git branch --set-upstream-to=origin/master master

echo "Installing Docker"
cd ~/
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh

echo "Set non sudo perms on docker commands..."
sudo usermod -aG docker pi


echo "Setup Complete"
