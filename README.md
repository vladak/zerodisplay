[![Python checks](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml/badge.svg)](https://github.com/vladak/zerodisplay/actions/workflows/python-checks.yml)

# zerodisplay

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
  sudo cp /srv/weather/zerodisplay.service /etc/systemd/system/
  sudo systemctl enable zerodisplay
  sudo systemctl daemon-reload
  sudo systemctl start zerodisplay
  sudo systemctl status zerodisplay
```