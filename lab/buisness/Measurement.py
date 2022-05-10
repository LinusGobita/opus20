import logging

from lab.buisness.common import Constants
from lab.buisness.tools import Logger


class Measure:
    def __init__(self, channel, value):
        self.channel = channel
        self.value = value

def measure(opus20):

    full_measure = []

    try:
        opus20.connect()
        print(f"Measure on Host: {opus20.host} ")
        for channel in opus20.channels:
            value = opus20.channel_value(channel)
            measure = Measure(channel, value)
            full_measure.append(measure)

        for measure in full_measure:
            Logger.log_measure(opus20.host, measure.channel, measure.value)
            Logger.print_measure(opus20.host, measure.channel, measure.value)

        opus20.disconnect()
        return full_measure

    except Exception as err:
        Logger.log_warning("Measurement", opus20.host, err)
