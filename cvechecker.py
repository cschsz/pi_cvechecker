#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import datetime
import schedule
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests as req
import pickle
import time

#"https://www.cvedetails.com/json-feed.php?vendor_id=33&product_id=47&version_id=194147&numrows=30&year=2012"

url_3_18_14 = ["https://www.cvedetails.com/vulnerability-list.php?vendor_id=33&product_id=47&version_id=194147&page=1&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&month=0&cweid=0&order=1&trc=54&sha=e856f0294fda1cb68c232f5adb0ee7e79a7c426e",
               "https://www.cvedetails.com/vulnerability-list.php?vendor_id=33&product_id=47&version_id=194147&page=2&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&month=0&cweid=0&order=1&trc=66&sha=7e081e66188691d3dd7bac57f4531821702dc570"]

#----------------------------[log_info]
def log_info(info):
    print("[log] " + info)
    try:
        f = open("/var/log/cvechecker.log","a")
    except PermissionError:
        f = open("cvechecker.log","a")
    f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + info + "\r\n")
    f.close()
    return

#----------------------------[send_mail]
def send_mail(message):
    # read config
    config = configparser.ConfigParser()
    config.read('/usr/local/etc/cvechecker.ini')
    try:
        host  = config["EMAIL"]["SMPT_HOST"]
        port  = config["EMAIL"]["SMPT_PORT"]
        email = config["EMAIL"]["SMPT_EMAIL"]
        passw = config["EMAIL"]["SMPT_PASSWORD"]
        dest  = config["EMAIL"]["DESTINATION_EMAIL"]
    except KeyError:
        log_info("cvechecker.ini not filled")
        return -1

    # email login
    try:
        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(email, passw)
    except Exception:
        log_info("SMTP error: " + traceback.format_exc())
        return -1

    # prepare email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "cvechecker"
    msg['From'] = email
    msg['To'] = dest

    html = """
    <head></head>
    <body>
        %s
    </body>
    """ % message
    msg.attach(MIMEText(html, 'html'))

    # send email
    try:
        s.sendmail(email, dest, msg.as_string())
        s.quit()
        log_info("email send")
    except Exception as e:
        log_info("SMTP error:" + e)
        return -1

    return 0

#----------------------------[readfile]
def readfile(filename):
    array=[]
    try:
        with open (filename, 'rb') as fp:
            array = pickle.load(fp)
    except Exception:
        pass
    return array

#----------------------------[getreadurlold]
def readurl(url, array):
    try:
        resp = req.get(url)
    except Exception:
        log_info("error reading url: {:.120s}...".format(url))
        return -1

    string = resp.text
    pos = 0
    while True:
        pos = string.find(">CVE-", pos)
        if pos == -1:
            break
        pos += 1
        end = string.find("<", pos)
        array.append(string[pos:end])
    
    return 0

#----------------------------[getreadurlold]
def getnew(old, cve, new):
    result = ""
    for i in range(0, len(cve)):
        try:
            old.index(cve[i])
        except ValueError:
            new.append(cve[i])
            result += "new: " + cve[i] + "<br>"
    return result

#----------------------------[getreadurlold]
def checkcve(file, urls):
    message = ""
    new=[]
    cve=[]

    old = readfile(file)
    for url in urls:
        ret = readurl(url, cve)
        if ret:
            message += "error reading url: {:.120s}...<br>".format(url)

    message += getnew(old, cve, new)
    log_info("{:d} old".format(len(old)))
    log_info("{:d} cve".format(len(cve)))
    log_info("{:d} new".format(len(new)))
        
    if len(message):
        message += "<p>{:s}</p>".format(file)
        ret = send_mail(message)
        if ret == 0:
            with open(file, 'wb') as fp:
                pickle.dump(cve, fp)
    return

#----------------------------[once_a_day]
def once_a_day():
    log_info("once_a_day")
    checkcve("3_18_14.lst", url_3_18_14)
    return    

#----------------------------[]     
if __name__=='__main__':
    log_info("starting")
    once_a_day()
    schedule.every().day.at("08:00").do(once_a_day)
    try:
        while True:
            schedule.run_pending()
    except:
        log_info("exit")