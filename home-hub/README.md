# Home Hub

## Getting the RPi up and running with the Home Hub code

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

### OPTIONAL - Install `vim`
```bash
sudo apt-get install vim
```

### Running the HH
```bash
python init.py  # pass -d flag to run in DEBUG mode, which in turn also prints logs to stdout
```