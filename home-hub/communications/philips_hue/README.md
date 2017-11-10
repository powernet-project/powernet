# Philips Hue Control

TODO:
----
- Add error reporting
- Add local logger

## Python script that long polls the PwrNet server for changes requested to the lighting in the home
### Script is meant to run in a BeagleBone Black / RaspberryPi, it may however run on your *nix machine
### Highly rec. running this in an virtualenv!

### lib dep is only requests
```
pip install requests
```

### run the script
```
python poll-hue-changes.py
```

### alternative setup and options
```
virtualenv venv_hue
source venv_hue/bin/activate
pip install requests
nohup python poll-hue-changes.py & exit
```

### You may also leverage the virtualenv at the home_hub level as opposed to creating this separate one! 