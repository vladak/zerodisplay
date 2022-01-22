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
  sudo apt-get install -y python3-pip
  sudo pip3 install adafruit-circuitpython-epd
  sudo apt-get install -y fonts-dejavu
  sudo apt-get install -y python3-pil
```
- checkout the Git repository
```
  mkdir /srv
  git clone https://github.com/vladak/zerodisplay /srv/zerodisplay
```
- enable+start the service
```
  sudo cp /srv/weather/zerodisplay.service /etc/systemd/system/
  sudo systemctl enable zerodisplay
  sudo systemctl daemon-reload
  sudo systemctl start zerodisplay
  sudo systemctl status zerodisplay
```