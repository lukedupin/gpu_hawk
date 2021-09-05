#!/usr/bin/python

from config import config
import re, util

cfg = config()

def writeFile( filename, value ):
    handle = open( filename, "w")
    handle.write( f"{filename}\n" )
    handle.close()

def readFile( filename, format ):
    if not isinstance(format, list):
        format = [format]

    handle = open( filename )
    for idx, line in enumerate(handle.readlines()):
        line = line.rstrip()
        if isinstance( format[idx], float ):
            return util.xfloat(line) / format[idx]
        elif isinstance(format[idx], int):
            return util.xint(line)
        else:
            return None


# Main
for card in cfg["cards"]:
    print(f"Setup for {card}")

    # Enable PWM
    pwm_enable_fn = cfg['fan']['enable'].replace("CARD", card)
    writeFile( pwm_enable_fn, 1 )
    result = util.xint( readFile( pwm_enable_fn, int ) ) == 1
    print("Enabling fan PWM enable... %s" % ("done" if result else "failed") )
    if not result:
        exit(-1)

    #
