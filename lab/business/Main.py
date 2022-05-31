import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from lab.business import Measurement
from lab.business.common import Constants
from lab.business.tools import Logger
from lab.persistence import DatabaseWriter


if __name__ == '__main__':
    time_settings = Constants.get_settings_time()
    opus20List = Constants.get_opus20_data()

    def measure_all_opus20():
        measure_time = datetime.now().strftime("%Y-%m-%d %H:%M:00.000")

        for opus20 in opus20List:
            measure_one_host = Measurement.measure(opus20)

            #Queck Date Time
            DatabaseWriter.write_time_to_db(measure_time)
            DatabaseWriter.write_measure_to_db(opus20, measure_time, measure_one_host)


    # BlockingScheduler: use when the scheduler is the only thing running in your process
    scheduler = BlockingScheduler()

    # Schedules the job_function to be executed Monday through Friday at between 12-16 at specific times.
    try:
        scheduler.add_job(measure_all_opus20, 'cron', day_of_week=time_settings[0], hour=time_settings[1], minute=time_settings[2], start_date=time_settings[3], timezone=time_settings[4])
    except Exception as err:
        Logger.log_error("Main", err)

    # Start the scheduler
    scheduler.start()

    #Cannot insert the value NULL into column 'idChannel', table 'weatherdata.dbo.value'; column does not allow nulls. INSERT fails.