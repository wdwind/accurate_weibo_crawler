# -*- coding: utf-8 -*-

from colorama import init
import time
import sys

try:
    import lcd
    lcd = lcd.lcd()
    # Change this to your i2c address
    lcd.set_addr(0x23)
except:
    lcd = False

init()

def log(string, color = 'white'):
    colorHex = {
        'green': '92m',
        'yellow': '93m',
        'red': '91m'
    }
    string = unicode(string)
    sse = sys.stdout.encoding
    string = string.encode(sse, "replace").decode(sse)
    if color not in colorHex:
        print('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] '+ string)
    else:
        print(u'\033['+ colorHex[color] + '[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] ' + string + '\033[0m')
    if lcd:
        if(string):
            lcd.message(string)
