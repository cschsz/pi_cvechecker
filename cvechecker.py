#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests as req

url_3_18_14 = ["https://www.cvedetails.com/vulnerability-list.php?vendor_id=33&product_id=47&version_id=194147&page=1&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&month=0&cweid=0&order=1&trc=54&sha=e856f0294fda1cb68c232f5adb0ee7e79a7c426e",
               "https://www.cvedetails.com/vulnerability-list.php?vendor_id=33&product_id=47&version_id=194147&page=2&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&month=0&cweid=0&order=1&trc=66&sha=7e081e66188691d3dd7bac57f4531821702dc570"]

new = 0
found = 0
for url in url_3_18_14:
    resp = req.get(url)
    string = resp.text
    pos = 0
    while True:
        pos = string.find(">CVE-", pos)
        if pos == -1:
            break
        pos += 1
        end = string.find("<", pos)
        cve = string[pos:end]
        print(cve)
        found += 1
print("{:d} CVE".format(found))
