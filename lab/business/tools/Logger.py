import logging
import os
import time
import sys
from datetime import datetime
from lab.business.common import Constants


logfile_path = ""

def create_logfile(path):
    logfile_path = path
    os.makedirs(path)



def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def log_error(class_name, err, id):
    logging.warning(f"Error:{id} Klassen: {class_name} error: {err} <=================")

def log_warning(class_name, host, err, id):
    logging.warning(f"WARNING:{id} Klassen: {class_name} host: {host} error: {err}")
    print(f"WARNING:{id}  Klassen: {class_name} host: {host} error: {err}")

def log_measure(host, channel, value):
    logging.info(f"Measure:{id} host: {host}, channel, {channel}, value, {value}")

def print_measure(host, channel, value):
    print(f"{get_time()}     Measure: host: {host}, channel, {channel}, value, {value}")

def print_sleeptime(timer):
    t = timer

    while t != 0:
        print(f"Take a Coffe for {t} secounts", end=' ')
        time.sleep(1)
        print(end='\r')
        t -= 1
    print("------------------------------------------------------------")
    print(f'{get_time()} New measure')
    print("------------------------------------------------------------")

