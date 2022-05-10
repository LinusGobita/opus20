import logging

from lab.buisness.common import Constants


def log_error(class_name, err):
    logging.warning(f"Error: Klassen: {class_name} error: {err}")

def log_warning(class_name, host, err):
    logging.warning(f"WARNING: Klassen: {class_name} host: {host} error: {err}")


def log_measure(host, channel, value):
    logging.info(f"Measure: host: {host}, channel, {channel}, value, {value}")


