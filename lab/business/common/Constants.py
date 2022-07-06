import json
import logging
import shutil
from datetime import datetime
import configparser
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
settings_file_name = "/Settings.ini"

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
setting_file = abs_path_constants + settings_file_name
opus20_data_path = abs_path_constants + opus20_file_name

if not os.path.exists(abs_path_constants):
    shutil.copytree(abs_path_files_app, abs_path_use_constants)
    logging.info(f"Create Path {abs_path_constants}")

if not os.path.exists(abs_path_logs):
    os.makedirs(abs_path_logs)
    logging.info(f"Create Path {abs_path_logs}")

#logging.basicConfig(
#    level=logging.WARNING,
#    filename=log_file,
#    filemode="a+",
#    format="%(asctime)-15s — %(levelname)s\t— %(name)s\t— %(message)s"
#    )

def open_json_file(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except Exception as err:
        logging.error(err)

def open_file_as_string(path):
    try:
        with open(path) as f:
            data = f.read()
        return data
    except Exception as err:
        logging.error(err)


def open_txt_file(path):
    try:
        with open(path) as f:
            data = f.read()
            score_ints = [int(x) for x in data.split()]
        return score_ints
    except Exception as err:
        logging.error(err)

def get_opus20_data():
    path = abs_path_constants + opus20_file_name

    opus20_list = []
    data = open_json_file(opus20_data_path)
    try:
        for opus20 in data:
            opus20 = Opus20(opus20["host"],opus20["channels"], opus20["mac"], opus20["labor"], opus20["location"])
            opus20_list.append(opus20)
    except Exception as err:
        logging.error(err)

    return opus20_list

def read_from_json_array(json, id, name):
    obj = json[id][name]
    return obj

def get_logging_level():
    string = open_file_as_string(setting_file)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(string)

    return config["setting_programm"]["logging_level"]

def get_settings_time():
    time_settings = []
    string = open_file_as_string(setting_file)

    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(string)

    time_settings.append(config["setting_time"]["day_of_week"])
    time_settings.append(config["setting_time"]["hour"])
    time_settings.append(config["setting_time"]["minute"])
    time_settings.append(config["setting_time"]["start_date"])
    time_settings.append(config["setting_time"]["timezone"])

    return time_settings


def get_settings_database():
    database_settings = []
    string = open_file_as_string(setting_file)

    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(string)

    database_settings.append(config["databse"]["host"])
    database_settings.append(config["databse"]["name"])
    database_settings.append(config["databse"]["user"])
    database_settings.append(config["databse"]["passwort"])
    database_settings.append(config["databse"]["driver"])
    database_settings.append(config["databse"]["trusted_connection"])

    return database_settings

"""
#Andere Variante suchen. nicht über data[0] zugreifen
def get_settings_time():
    try:
        data = get_settings_all()
        setiings_time_all = data[0]["setting_time"]
        time_settings = []

        for detai in setiings_time_all:
            time_settings.append(detai["day_of_week"])
            time_settings.append(detai["hour"])
            time_settings.append(detai["minute"])
            time_settings.append(detai["start_date"])
            time_settings.append(detai["timezone"])
    except Exception as err:
        logging.error(err)
    return time_settings

def get_settings_database():
    data = get_settings_all()
    try:
        setiings_time_all = data[1]["database"]
        database_settings = []

        for detai in setiings_time_all:
            database_settings.append(detai["host"])
            database_settings.append(detai["name"])
            database_settings.append(detai["user"])
            database_settings.append(detai["passwort"])
            database_settings.append(detai["driver"])
            database_settings.append(detai["trusted_connection"])
    except Exception as err:
        logging.error(err)
    return database_settings
"""