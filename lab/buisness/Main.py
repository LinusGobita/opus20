import time

from lab.buisness import Measurement
from lab.buisness.common import Constants
from lab.buisness.tools import Logger

if __name__ == '__main__':

    while True:
        sleep_time = Constants.get_MeasurementTimeIntervalInSeconds()

        opus20List = Constants.get_opus20_data()
        offlineHost = []

        for opus20 in opus20List:
            Measurement.measure(opus20)

        Logger.print_sleeptime(sleep_time)


""""
    # Ist das Gerät Online?
    for opus20 in opus20List:
        status = Checker.check_connection_opus20(opus20)
        if status != 0:
            offlineHost.append(opus20)

    Logger.clear_console()

    if offlineHost:
        print(f"Warnung: folgende Host sind nicht erreichbar:")
        for opus20 in offlineHost:
            print(opus20.host)
            opus20List.remove(opus20)
"""
