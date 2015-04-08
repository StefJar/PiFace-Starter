# PiFace-Starter
a application starter for the PiFace Control and Display

# start at boot

open consol at your RPi and enter 
```
sudo crontab -e
```
add at the end of the file
```
@reboot python3 /home/pi/PiFaceStarter.py -p"/home/pi" &
```

this is based on the tutorial from [Ioannis Kedros](http://embeddedday.com/projects/raspberry-pi/a-step-further/running-python-script-at-boot/)