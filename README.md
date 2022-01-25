[![Python checks](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml/badge.svg)](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml)

# zerodisplay

The goal of this tiny project is to display outside temperature and a few other metrics (CO2, atmospheric pressure) on a display attached to a fridge. This assume this data is already collected elsewhere and available via HTTP. Specifically this assumes https://github.com/vladak/weather.

## Hardware

- [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)
- [Adafruit 2.13" Monochrome E-Ink Bonnet](https://www.adafruit.com/product/4687)
- Apple Magic mouse.. wait for it.. transparent enclosure
- a nice drawing

It looks like this: ![Magic enclosure](/magic_enclosure.jpg)

The buttons are currently unused, might drill the holes for them one day, in order to be able to switch to e.g. a name-of-the-day display. Similarly, if the Pi tends to overheat, will have to drill some holes to the top of the enclosure.

## Install

per https://learn.adafruit.com/2-13-in-e-ink-bonnet/usage

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
- enable+start the service
```
  sudo cp /srv/zerodisplay/zerodisplay.service /etc/systemd/system/
  sudo systemctl enable zerodisplay
  sudo systemctl daemon-reload
  sudo systemctl start zerodisplay
  sudo systemctl status zerodisplay
```
