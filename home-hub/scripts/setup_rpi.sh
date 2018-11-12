#!/bin/bash

echo "Installing Docker"
cd ~/
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh

echo "Set non sudo perms on docker commands..."
sudo usermod -aG docker pi

echo "Setup Complete"
