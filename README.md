# cvechecker
parses cvedetails.com for new CVEs

Programm logging is found in /var/log/cvechecler.log

## Preparation
```
sudo apt-get install python3-rpi.gpio python3-pip
sudo pip3 install schedule requests
```
## Running
```
python3 cvechecker.py
```
If already "installed" execute this before running from console:
```
ps -aux | grep  python3 /usr/local/bin/cvechecker.py
sudo kill [pid]
```

### optional hardware layout
http://rpi.science.uoit.ca/lab/gpio/
```
2   4   6   8   10  12  14  16  18  20  22  24  26  28  30  32  34  36  38  40
1   3   5   7   9   11  13  15  17  19  21  23  25  27  29  31  33  35  37  39
                                                                        |   |
                                                                        |   ^
                                                                       1k0  |
                                                                        |   ^
                                                                       LED  |
                                                                        +---+
```

## Installation
```
sudo chmod +x install.sh
./install.sh
```
for email notification fill the variables in /usr/local/etc/cvechecker.ini

add in /etc/rc.local before the last line (exit 0):
```
/usr/local/bin/cvechecker.py &
```
