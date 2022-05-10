from lab.buisness import Measurement
from lab.buisness.common import Constants


if __name__ == '__main__':

    print(Constants.log_file)

    opus20List = Constants.get_opus20_data()
    offlineHost = []

    for opus20 in opus20List:
        Measurement.measure(opus20)

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
