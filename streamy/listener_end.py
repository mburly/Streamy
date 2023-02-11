import os
import psutil
import time

import mysql.connector

from .utils import Config

c = Config()
if(os.name == 'nt'):
    PROC_NAME = "mpv.exe"
else:
    PROC_NAME = "mpv"

def isRequestFulfilled():
    db = mysql.connector.connect(
            host=c.dbHost,
            user=c.dbUser,
            password=c.dbPassword,
            database=c.dbName
        )
    cursor = db.cursor()
    sql = f'SELECT done FROM requests ORDER BY id DESC LIMIT 1;'
    cursor.execute(sql)
    try:
        done = cursor.fetchone()[0]
    except:
        return True
    cursor.close()
    db.close()
    if done is None:
        return False
    return True if done == 1 else False

def listenForFulfilledRequest():
    stream_running = True
    while(stream_running):
        try:
            if(isRequestFulfilled()):
                killMpv()
                stream_running = False
        except:
            return None
        time.sleep(5)

def killMpv():
    for proc in psutil.process_iter():
        if proc.name() == PROC_NAME:
            try:
                proc.kill()
            except:
                return None


def run():
    try:
        print('Listening for fulfilled requests...')
        while True:
            print('[PING] listener_end.py')
            listenForFulfilledRequest()
    except KeyboardInterrupt:
        return None
