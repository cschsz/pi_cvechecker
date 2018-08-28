#!/bin/bash
sudo cp -n cvechecker.ini /usr/local/etc
sudo mkdir /usr/local/bin/cvechecker
sudo cp *.py /usr/local/bin/cvechecker
sudo chmod +x /usr/local/bin/cvechecker/cvechecker.py
sudo rm /var/log/cvechecker.log
sudo reboot
