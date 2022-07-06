import logging
import mariadb
import sys
from lab.business.common import Constants

database_conn = Constants.get_settings_database()

def mysql_connect():
    global cur, conn
    try:
        conn = mariadb.connect(
            user=database_conn[2],
            password=database_conn[3],
            host=database_conn[0],
            port=3306,
            database=database_conn[1]
        )
    except mariadb.Error as e:
        logging.error(e)
    cur = conn.cursor()

def mysql_disconnect():
    conn.commit()
    conn.close()

def write_measure_to_db(opus20, datetime, measures):
    print("NEW MEWASURE " + datetime)
#    mysql_connect()
    for measure in measures:
        print(f"INSERT INTO  'Labor.wetmeasureoe' ('iID', 'timeStamp', 'measureShortcut', 'value')"
              f"VALUES('{opus20.mac}', '{datetime}', '{measure.channel}', '{measure.value}')")

