import json
import logging
import shutil
from lab.business.tools import Logger
from datetime import datetime
from opus20 import Opus20
import os

date_str = datetime.now().strftime("%Y-%m-%d")
sub_dir = "opus20"

# Folder
sub_dir_opus20 = "opus20_data"
sub_dir_logs = "logs"
sub_dir_common = "common"

# File Name
log_file_name = f"logfile_{date_str}.txt"
opus20_file_name = "/Opus20.json"
settings_file_name = "/Settings.json"

# absulte Path
abs_path_desktop = os.path.expanduser(f"~/Desktop/")
abs_path_app = os.path.join(sub_dir)
abs_path_files = os.path.join(abs_path_app, sub_dir, "/files")
abs_path_constants = os.path.join(abs_path_desktop, sub_dir_opus20)
abs_path_logs = os.path.join(abs_path_desktop, sub_dir_opus20, sub_dir_logs)

# Files
log_file = os.path.join(abs_path_desktop, sub_dir_opus20, sub_dir_logs, log_file_name)

if not os.path.exists(abs_path_constants):
    os.makedirs(abs_path_constants)
#        shutil.copy("/Users/linusgobita/PycharmProjects/opus20/files/Opus20.json", abs_path_constants + opus20_file_name)
#        shutil.copy("/Users/linusgobita/PycharmProjects/opus20/files/Settings.json", abs_path_constants + channels_file_name)


if not os.path.exists(abs_path_logs):
    os.makedirs(abs_path_logs)

logging.basicConfig(
    level=logging.DEBUG,
    filename=log_file,
    filemode="a+",
    format="%(asctime)-15s %(message)s"
)


def get_logfile():
    return log_file


def open_json_file(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data

    except Exception as err:
        Logger.log_error("Constants", err)


def open_txt_file(path):
    try:
        with open(path) as f:
            data = f.read()
            score_ints = [int(x) for x in data.split()]
        return score_ints

    except Exception as err:
        Logger.log_error("Constants", err)


def get_opus20_data():
    path = abs_path_constants + "/" + opus20_file_name
    opus20_list = []
    data = open_json_file(path)

    for opus20 in data:
        opus20 = Opus20(opus20["host"],opus20["channels"], opus20["mac"], opus20["labor"], opus20["location"])
        opus20_list.append(opus20)

    return opus20_list

def get_settings():
    path = abs_path_constants + "/" + settings_file_name
    data = open_json_file(path)
    return data

def get_MeasurementTimeIntervalInSeconds():
    settings = get_settings()
    return settings["MeasurementTimeIntervalInSeconds"]


class Settings(object):
    def __init__(self, MeasurementTimeIntervalInSeconds):
        self.MeasurementTimeIntervalInSeconds = MeasurementTimeIntervalInSeconds


"""
    for chanel in data:
        chanel_list = ["temperature"], ["humidity"], ["dewpoint"], ["air preassure"], ["batterie voltage"]
        
        #channel_list = [int(i) for i in data.split() if i.isdigit()]

    #temp = re.findall(r'\d+', data)
    #channel_list = [100, 200, 300]
"""

#    for opus20 in data["opus20"]:
#        opus20 = opus20["host"], opus20["mac"], opus20["labor"], opus20["location"]


#        opus20List.append(Opus20(opus20["host"], opus20["mac"], opus20["labor"], opus20["location"]))

#    for opus20Json in data["opus20"]:
#
#        opus20 = Opus20
#
#        opus20.host = opus20Json["host"]
#        opus20.mac = opus20Json["mac"]
#        opus20.labor = opus20Json["labor"]
#        opus20.location = opus20Json["location"]

#        opus20List.append(opus20)
