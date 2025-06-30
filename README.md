[![Python checks](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml/badge.svg)](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml)

# zerodisplay

The goal of this tiny project is to display outside temperature and a few other metrics (CO2, atmospheric pressure) on a display attached to a fridge. This assume this data is already collected elsewhere and available via HTTP. Specifically this assumes https://github.com/vladak/weather.

## Hardware

- [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)
- ~[Adafruit 2.13" Monochrome E-Ink Bonnet](https://www.adafruit.com/product/4687)~ [Pimoroni Inky pHAT - eInk Display - Black/White](https://www.adafruit.com/product/3934)
- Apple Magic mouse.. wait for it.. transparent enclosure
- a nice drawing

It looks like this: ![Magic enclosure](/magic_enclosure.jpg)

The buttons on the Adafruit were left unused. I considered drilling the holes for them one day, in order to be able to switch to e.g. a name-of-the-day display. Similarly, if the Pi tends to overheat, will have to drill some holes to the top of the enclosure. Over the time (3 years or so) the original Adafruit display become dimmer, up to the point when it was a bit hard to read from distance, so I replaced it with the Pimoroni inky pHAT. The same driver can be used to drive it and it has the same resolution, so it was just a matter of swapping it. The Pimoroni display has to STEMMA QT connector or buttons, which I did not used anyway.

## Install

- initial setup: https://github.com/vladak/pirig/blob/master/common.md
- disable not needed services
```
# Bluetooth
sudo apt-get purge bluez -y
sudo apt-get autoremove -y
```
- enable SPI (in the `Interfaces` menu):
```
sudo raspi-config
```
- check there are some `/dev/spidev0.*` devices
- install pre-requisites
```
  sudo apt-get install -y python3-venv
  sudo apt-get install -y fonts-dejavu
  sudo apt-get install -y libopenjp2-7 # needed for Pillow
  sudo apt-get install -y libatlas-base-dev # needed for numpy used by prometheus-api-client
  sudo apt-get install -y libjpeg9 # to build Pillow wheel
```
- checkout the Git repository
```
  [[ ! -d srv ]] || mkdir /srv
  sudo chown pi /srv
  sudo apt-get install -y git
  git clone https://github.com/vladak/zerodisplay /srv/zerodisplay
```
- install requirements:
```
  cd /srv/zerodisplay
  python3 -m venv env
  . ./env/bin/activate
  export CFLAGS=-fcommon # needed for RPi.GPIO per https://askubuntu.com/a/1330210
  pip install -r requirements.txt
```
- configure the service: create `/srv/zerodisplay/environment` file and setup these environment variables inside:
  - `ARGS`: arguments to the `report` program
  - the file can look like this (no double quotes):
```
ARGS=-U http://localhost:8111 -l debug --temp_sensor_name foo/bar
```
- enable+start the service
```
  sudo cp /srv/zerodisplay/zerodisplay.service /etc/systemd/system/
  sudo systemctl enable zerodisplay
  sudo systemctl daemon-reload
  sudo systemctl start zerodisplay
  sudo systemctl status zerodisplay
```

# Links

- https://learn.adafruit.com/2-13-in-e-ink-bonnet/usage
- https://learn.pimoroni.com/article/getting-started-with-inky-phat
