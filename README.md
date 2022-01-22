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
# TODO: what to do with the font ?
wget https://github.com/adafruit/Adafruit_CircuitPython_framebuf/raw/main/examples/font5x8.bin
sudo apt-get install -y fonts-dejavu
sudo apt-get install -y python3-pil


```
