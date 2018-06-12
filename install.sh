#!/bin/bash
sudo cp -n cvechecker.ini /usr/local/etc 
sudo cp cvechecker.py /usr/local/bin
sudo chmod +x /usr/local/bin/cvechecker.py
sudo rm /var/log/cvechecker.log
