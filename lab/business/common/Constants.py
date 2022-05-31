import json
import logging
import shutil
import time

from lab.business.tools import Logger
from datetime import datetime
from opus20 import Opus20
import os

date_str = datetime.now().strftime("%Y-%m-%d")
sub_dir = "opus20"

# Folder
sub_dir_opus20 = "opus20_settings"
sub_dir_logs = "logs"
sub_dir_common = "common"

# File Name
log_file_name = f"logfile_{date_str}.txt"
opus20_file_name = "/Opus20.json"
settings_file_name = "/Settings.json"

# absulte Path
abs_path_opus20_app = os.getcwd()
abs_path_desktop = os.path.expanduser(f"~/Desktop/")
abs_path_app = os.path.join(sub_dir)
abs_path_files = os.path.join(abs_path_app, sub_dir, "/opus20_settings")
abs_path_constants = os.path.join(abs_path_desktop, sub_dir_opus20)
abs_path_logs = os.path.join(abs_path_desktop, sub_dir_opus20, sub_dir_logs)

abs_path_files_app = os.path.join(abs_path_opus20_app, sub_dir_opus20)
abs_path_use_constants = os.path.join(abs_path_desktop, sub_dir_opus20)
# Files
log_file = os.path.join(abs_path_desktop, sub_dir_opus20, sub_dir_logs, log_file_name)

if not os.path.exists(abs_path_constants):
    shutil.copytree(abs_path_files_app, abs_path_use_constants)

#        shutil.copy("/Users/linusgobita/PycharmProjects/opus20/opus20_settings/Opus20.json", abs_path_constants + opus20_file_name)
#        shutil.copy("/Users/linusgobita/PycharmProjects/opus20/opus20_settings/Settings.json", abs_path_constants + channels_file_name)

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
        Logger.log_error("Constants", err, 3)


def open_txt_file(path):
    try:
        with open(path) as f:
            data = f.read()
            score_ints = [int(x) for x in data.split()]
        return score_ints

    except Exception as err:
        Logger.log_error("Constants", err)


def get_opus20_data():
    path = abs_path_constants + opus20_file_name
    opus20_list = []
    data = open_json_file(path)

    for opus20 in data:
        opus20 = Opus20(opus20["host"],opus20["channels"], opus20["mac"], opus20["labor"], opus20["location"])
        opus20_list.append(opus20)

    return opus20_list


def get_settings_all():
    path = abs_path_constants + settings_file_name
    data = open_json_file(path)
    return data

def read_from_json_array(json, id, name):
    obj = json[id][name]
    return obj


def get_settings_time():
    data = get_settings_all()
    setiings_time_all = data[0]["setting_time"]
    options = ["day_of_week", "hour", "minute", "start_date", "timezone"]
    time_settings = []
    i = 0

    for detai in setiings_time_all:
        time_settings.append(detai["day_of_week"])
        time_settings.append(detai["hour"])
        time_settings.append(detai["minute"])
        time_settings.append(detai["start_date"])
        time_settings.append(detai["timezone"])

    return time_settings



def get_settings_time():
    data = get_settings_all()
    setiings_time_all = data[0]["setting_time"]
    time_settings = []

    for detai in setiings_time_all:
        time_settings.append(detai["day_of_week"])
        time_settings.append(detai["hour"])
        time_settings.append(detai["minute"])
        time_settings.append(detai["start_date"])
        time_settings.append(detai["timezone"])

    return time_settings



def get_settings_database():
    data = get_settings_all()
    setiings_time_all = data[1]["database"]
    database_settings = []

    for detai in setiings_time_all:
        database_settings.append(detai["host"])
        database_settings.append(detai["name"])
        database_settings.append(detai["user"])
        database_settings.append(detai["passwort"])
        database_settings.append(detai["driver"])
        database_settings.append(detai["trusted_connection"])

    return database_settings




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
