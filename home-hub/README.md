# Home Hub

## Getting the RPi up and running with docker and the Home Hub code

### After you've SSH'ed into the RPi, update its OS:
```bash
sudo -s
apt update && apt upgrade && apt dist-upgrade
rpi-update && reboot
```

### In the home dir `~/`, run the following commands:
```bash
mkdir HomeHub
cd HomeHub
git init
git config core.sparsecheckout true # allows us to checkout only a portion of the repo
echo home-hub/ >> .git/info/sparse-checkout # defines which part of the repo we want to check out
git remote add -f origin https://github.com/powernet-project/powernet.git
git pull origin master
git branch --set-upstream-to=origin/master master
```

### Install Docker on the RPi:
```bash
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
```

### Allow docker usage w/o sudo
```bash
sudo usermod -aG docker pi
```

### OPTIONAL - Install `vim`
```bash
sudo apt-get install vim
```

