#!/bin/bash

# recommended - change mirror
# see https://www.raspbian.org/RaspbianMirrors
sudo nano /etc/apt/sources.list
sudo apt update

# pre-requistes in /boot/config.txt:
# dtparam=i2c_arm=on
# dtoverlay=imx219
# dtoverlay=pwm,pin=12,func=4
# dtparam=act_led_gpio=22

sudo sh -c "echo i2c-dev >> /etc/modules"

sudo apt install -y git cmake gcc g++
sudo apt install -y zram-tools
sudo apt install -y libjpeg-dev

# Setup camera-streamer
PACKAGE=camera-streamer-$(test -e /etc/default/raspberrypi-kernel && echo raspi || echo generic)_0.2.8.$(. /etc/os-release; echo $VERSION_CODENAME)_$(dpkg --print-architecture).deb
wget "https://github.com/ayufan/camera-streamer/releases/download/v0.2.8/$PACKAGE"
sudo apt install "$PWD/$PACKAGE"

# Setup mjpg-streamer
git clone https://github.com/jacksonliam/mjpg-streamer
cd mjpg-streamer/mjpg-streamer-experimental/
make
sudo make install

# python requirements
sudo apt install -y python3-pip python3-bottle python3-plac python3-scipy python3-smbus python3-matplotlib python3-dbus python3-colour
sudo pip3 install rpi-hardware-pwm

# web service
sudo apt install -y nginx
sudo cp ~/nginx/sites-available/default /etc/nginx/sites-available/default
sudo systemctl restart nginx.service

# setup services
# services contain all options for camera/mjpg streamers
sudo cp services/system/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bottleweb.service
sudo systemctl enable camera-streamer.service
sudo systemctl enable thermal-camera-streamer.service
# Started manually so not enabled
#sudo systemctl enable amg8833.service

# recommended
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
sudo apt install ufw
sudo ufw allow 22
sudo ufw limit 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

