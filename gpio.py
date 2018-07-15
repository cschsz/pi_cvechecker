#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

try:
    from RPi.GPIO import *
    imp = True
except ImportError:
    imp = False
    #----------------------------[setmode]
    def setmode(board):
        return

    #----------------------------[BOARD]
    def BOARD():
        return

    #----------------------------[setup]
    def setup(led, state):
        return

    #----------------------------[OUT]
    def OUT():
        return

    #----------------------------[IN]
    def IN():
        return

    #----------------------------[LOW]
    def LOW():
        return 0

    #----------------------------[HIGH]
    def HIGH():
        return 1

    #----------------------------[output]
    def output(led, state):
        return

    #----------------------------[cleanup]
    def cleanup():
        return

pin_led = 37

#----------------------------[sirene]
def led(value):
    if value == 1:
        output(pin_led, HIGH)
    else:
        output(pin_led, LOW)
    return

#----------------------------[init]
def init():
    setmode(BOARD)
    setup(pin_led, OUT)

    led(1)
    return

#----------------------------[]
if __name__=='__main__':
    val = 0
    try:
        init()
        while True:
            led(val)
            if val == 1:
                val = 0
            else:
                val = 1
            time.sleep(1)
    except:
        pass
