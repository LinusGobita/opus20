import logging

from lab.business.common import Constants
from lab.business.tools import Logger


class Measure_singel:
    def __init__(self, channel, value):
        self.channel = channel
        self.value = value



def measure(opus20):
    full_measure_host = []

    try:
        opus20.connect()
#        print(f"Measure on Host: {opus20.host} ")
        for channel in opus20.channels:
            value = opus20.channel_value(channel)
            measure = Measure_singel(channel, value)
            full_measure_host.append(measure)

        opus20.disconnect()

        return full_measure_host

    except Exception as err:
        logging.warning(f"Measurement | channels: {err}")
        #Logger.log_warning("Measurement",33, opus20.host, err)

