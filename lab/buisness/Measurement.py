import logging

from lab.buisness.common import Constants
from lab.buisness.tools import Logger


class Measure:
    def __init__(self, channel, value):
        self.channel = channel
        self.value = value

def measure(opus20):

    chanells = Constants.get_channels()
    full_measure = []

    try:
        opus20.connect()

        for channel in chanells:
            value = opus20.channel_value(channel)
            measure = Measure(channel, value)
            full_measure.append(measure)

        for measure in full_measure:
            Logger.log_measure(opus20.host, measure.channel, measure.value)

        return full_measure

    except Exception as err:
        Logger.log_warning("Measurement", opus20.host, err)

