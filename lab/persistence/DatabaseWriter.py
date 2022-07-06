import logging
import time
import pyodbc

from lab.business.common import Constants

database_conn = Constants.get_settings_database()


def connect_ms_sql():
    try:
        conn = pyodbc.connect(
            f"Driver={database_conn[4]};"
            f"Server={database_conn[0]};"
            f"Database={database_conn[1]};"
            f"uid={database_conn[2]};"
            f"pwd={database_conn[3]};"
            f"TrustServerCertificate={database_conn[5]};"
        )
        cursor = conn.cursor()
        return cursor
    except Exception as err:
        logging.error(err)


def write_time_to_db(datetime):
    try:
        cursor = connect_ms_sql()
        logging.debug("Connect with db")
        query = cursor.execute(f'''
        use {database_conn[1]}
                        BEGIN
                            IF NOT EXISTS (SELECT datetime FROM time WHERE datetime = CONVERT(DATETIME, '{datetime}'))
                            BEGIN
                                INSERT INTO time(dateTime)
                                VALUES (CONVERT(DATETIME, '{datetime}'))
                            END
                        END
                           ''')
        query.commit()
        cursor.close()
        logging.debug("Disconnect with db")
    except Exception as err:
        logging.error(err)


def write_measure_to_db(opus20, datetime, measures):
    try:
        cursor = connect_ms_sql()
        for measure in measures:
            query = cursor.execute(f'''
            use {database_conn[1]}
                            INSERT INTO {database_conn[1]}.dbo.value(idDevice, idLocation, idMeasureTime, idMeasureType, value)
                            values 
                            (
                            (SELECT idDevice FROM device WHERE mac ='{opus20.mac}'),
                            (SELECT idLocation FROM location WHERE labor ='{opus20.labor}' AND location = '{opus20.location}'),
                            (SELECT idMeasureTime FROM time WHERE dateTime = CONVERT(DATETIME, '{datetime}')),
                            (SELECT idMeasureType FROM measureType WHERE channel ='{measure.channel}'), 
                            '{measure.value}'
                            )
                           ''')
        query.commit()
        cursor.close()
        logging.debug(f"save measre from host {opus20.host}")
    except Exception as err:
        logging.warning(err)


""""
INSERT INTO weatherdata.dbo.value(idDevice, idChannel, idLocation, idMeasure, value)
			values	(select idDevice from weatherdata.dbo.device where mac = '00:00:00:00:00'),
					(select idMesureType from weatherdata.dbo.mesureType where channel = '100'),
					(select idLocation from 

"""
