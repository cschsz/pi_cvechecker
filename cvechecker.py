#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import datetime
import schedule
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests as req
import gpio
import json
import pickle
import time

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
def send_mail(version, message):
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
    except Exception as e:
        log_info("SMTP error: " + str(e))
        return -1

    # prepare email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "cvechecker " + version
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
        log_info("SMTP error:" + str(e))
        return -1

    return 0

#----------------------------[checkdatabase]
def checkdatabase():
    try:
        resp = req.get("https://maxtruxa.com/cvedb-dev/api")
    except Exception:
        log_info("api: error reading db...")
        send_mail("api", "error reading db")
        return -1

    try:
        data = json.loads(resp.text)

        lupdate = data["last_update"]
        date = datetime.datetime.strptime(lupdate[:10], "%Y-%m-%d")
        ctime = datetime.datetime.today() - datetime.timedelta(days=2)
        if date < ctime:
            send_mail("api", "update error")
    except Exception as e:
        log_info("api: json error")
        send_mail("api", "json error")
        return -1

#----------------------------[readfile]
def readfile(filename):
    array=[]
    try:
        with open (filename, 'rb') as fp:
            array = pickle.load(fp)
    except Exception:
        pass
    return array

#----------------------------[readdb]
def readdb(version, array):
    url = "https://maxtruxa.com/cvedb-dev/api/cves?vendor=linux&product=linux_kernel&version={:s}".format(version)
    while True:
        try:
            resp = req.get(url)
        except Exception:
            log_info("{:s}: error reading db...".format(version))
            return -1

        try:
            data = json.loads(resp.text)
            for cve in data["cves"]:
                array.append(cve["id"])

            link = data["links"]
            url = link["next"]
            if url == None:
                break
        except Exception as e:
            log_info("{:s}: json error {:s}".format(version, str(e)))
            return -1

    if len(array) == 0:
        return -1
    else:
        return 0

#----------------------------[getnew]
def getnew(old, cve, new):
    result = ""
    newflag = False
    for i in range(0, len(cve)):
        try:
            old.index(cve[i])
        except ValueError:
            new.append(cve[i])
            result += "new: " + cve[i] + "<br>"
            newflag = True

    if newflag == True:
        result += "<p>{:d} old, {:d} cve, {:d} new</p>".format(len(old), len(cve), len(new))
    return result

#----------------------------[checkcve]
def checkcve(version):
    message = ""
    new=[]
    cve=[]

    # filename
    file = version
    file.replace(".", "_")
    file += ".lst"

    # read cve
    old = readfile(file)
    ret = readdb(version, cve)
    if ret:
        message += "error reading database...<br>"
        log_info("{:s}: error reading database".format(version))
    else:
        message += getnew(old, cve, new)
        log_info("{:s}: {:d} old, {:d} cve, {:d} new".format(version, len(old), len(cve), len(new)))

    # send mail
    if len(message) > 0:
        message += "<p>{:s}</p>".format(version)
        ret = send_mail(version, message)
        if ret == 0:
            with open(file, 'wb') as fp:
                pickle.dump(cve, fp)
    return

#----------------------------[once_a_day]
def once_a_day():
    log_info("once_a_day")

    checkdatabase()
    num = 1
    while True:
        config = configparser.ConfigParser()
        config.read('/usr/local/etc/cvechecker.ini')
        try:
            entry = "VERSION{:02d}".format(num)
            version  = str(config["CVE"][entry])
            version = version.strip("\"")
            checkcve(version)
            num += 1
        except KeyError:
            break

    return

#----------------------------[]
if __name__=='__main__':
    val = 0
    log_info("starting")
    gpio.init()
    once_a_day()
    schedule.every().day.at("08:00").do(once_a_day)
    try:
        while True:
            schedule.run_pending()
            gpio.led(val)
            if val == 1:
                val = 0
            else:
                val = 1
            time.sleep(1)
    except:
        log_info("exit")