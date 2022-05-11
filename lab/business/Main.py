import time

from lab.business import Measurement
from lab.business.common import Constants
from lab.business.tools import Logger

if __name__ == '__main__':

    while True:
        sleep_time = Constants.get_MeasurementTimeIntervalInSeconds()

        opus20List = Constants.get_opus20_data()
        offlineHost = []

        for opus20 in opus20List:
            Measurement.measure(opus20)

        Logger.print_sleeptime(sleep_time)
