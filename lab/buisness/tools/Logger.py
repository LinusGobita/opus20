import logging
import time
import sys
from datetime import datetime

from lab.buisness.common import Constants

now = datetime.now()
current_time = now. strftime("%H:%M:%S")

def log_error(class_name, err):
    logging.warning(f"Error: Klassen: {class_name} error: {err} <=================")

def log_warning(class_name, host, err):
    logging.warning(f"WARNING: Klassen: {class_name} host: {host} error: {err}")
    print(f"WARNING: Klassen: {class_name} host: {host} error: {err}")

def log_measure(host, channel, value):
    logging.info(f"Measure: host: {host}, channel, {channel}, value, {value}")

def print_measure(host, channel, value):
    print(f"{current_time}     Measure: host: {host}, channel, {channel}, value, {value}")

def print_sleeptime(timer):
    t = timer

    while t != 0:
        print(f"Take a Coffe for {t} secounts", end=' ')
        time.sleep(1)
        print(end='\r')
        t -= 1
    print("------------------------------------------------------------")
    print(f'{current_time}; Next Measure will Start')
    print("------------------------------------------------------------")

"""
# import the time module
import time

# define the countdown func.
def countdown(t):
    print("berak")
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print("r", timer, end="")
        time.sleep(1)
        t -= 1
    print('Fire in the hole!!')
"""

