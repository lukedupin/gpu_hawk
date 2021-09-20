#!/usr/bin/python

from config import config
import re, util, time

def replacer( filename, card ):
    for k in card.keys():
        filename = filename.replace(k.upper(), card[k])
    return filename

def writeFile( filename, card, value ):
    handle = open( replacer( filename, card ), "w")
    handle.write( f"{value}\n" )
    # handle.close()

def readFile( filename, card ):
    handle = open( replacer( filename, card ) )
    for idx, line in enumerate(handle.readlines()):
        return line.rstrip()

def calculateTemp( card, temps ):
    diff = None

    result = []
    for temp in temps:
        value = util.xfloat( readFile( temp['path'], card )) / 1000.0
        d = value - temp['target']

        # Returning None is automatic emergency shutdown level
        if value > temp['limit']:
            return (None, None, True)

        # Find the temp that is the hotest relative to the target
        if diff is None or diff < d:
            diff = d

        result.append( (temp['name'], int(round(value))) )

    return (diff, result, False)

# Start program

cfg = config()
fan_spd = [(cfg['fan']['start'], None) for _ in range(len(cfg["cards"]))]
hw_range = cfg['fan']['hw_range']
fan_range = cfg['fan']['range']
delay_drop = [0 for x in range(len(cfg["cards"]))]

# Configure initial fan and OC settings
for card in cfg["cards"]:
    start = cfg['fan']['start']
    print(f"Setup for {card['card']}")

    # Enable PWM
    writeFile( cfg['fan']['enable'], card, 1 )
    result = util.xint( readFile( cfg['fan']['enable'], card )) == 1
    print("    Enabling fan PWM enable for %s... %s" % (card['card'], "done" if result else "failed") )
    if not result:
        exit(-1)

    # Set initial fan speed
    print(f"    Setting {card['card']} speed: {int(round(start * 100))}%")
    raw = int((hw_range[1] - hw_range[0]) * start + hw_range[0])
    writeFile( cfg['fan']['control'], card, raw )

    # SEtup the OC profile

    print("")

# Fan loop
while True:
    print("")
    print("--------------------")

    temp_infos = []
    for idx, card in enumerate(cfg["cards"]):
        diff, temps, emergency = calculateTemp( card, cfg['temps'] )
        if emergency:
            print("SHUTDOWN!!!!")

        spd, last_diff = fan_spd[idx]

        change = 0
        if last_diff is not None:
            change = diff - last_diff

        #print(f"{diff} {last_diff} {change}")

        # Calc our new fan speed
        if diff >= 1.0 and change >= 0:
            spd += diff * cfg['fan']['step'] # Increase by the amount we're over
        elif diff <= -2.0 and change <= 0:
            delay_drop[idx] += 1
            if delay_drop[idx] >= cfg['delay_drop']:
                spd -= cfg['fan']['step'] # Decrease more consistently
                delay_drop[idx] 0

        # Cap the speed
        if spd < fan_range[0]:
            spd = fan_range[0]
        if spd > fan_range[1]:
            spd = fan_range[1]

        # Store the temps and speed
        temp_infos.append( (card, temps, spd) )

        # If the speed is the same, do nothing
        if spd == fan_spd[idx][0]:
            fan_spd[idx] = (spd, diff)
            continue
        fan_spd[idx] = (spd, diff)

        # Update the difference
        raw = int((hw_range[1] - hw_range[0]) * spd + hw_range[0])
        writeFile( cfg['fan']['control'], card, raw )
        print(f"Updating {card['card']} fan to {int(spd * 100.0)}%")

    # Dump our temp info
    for info in temp_infos:
        card, temps, fan = info
        print(f"Card: {card['card']}")
        print("    %-8s %d%%" % ("Fan", int(round(fan * 100.0))))
        for tmp in temps:
            print("    %-8s %dC" % (tmp[0], tmp[1]))

    time.sleep( cfg['update_rate'])
