import os
import psutil
import time

import mysql.connector

if(os.name == 'nt'):
    PROC_NAME = "mpv.exe"
else:
    PROC_NAME = "mpv"

def isRequestFulfilled():
    db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="streamy"
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
        if(isRequestFulfilled()):
            killMpv()
            stream_running = False
        time.sleep(5)

def killMpv():
    for proc in psutil.process_iter():
        if proc.name() == PROC_NAME:
            proc.kill()


def run():
    try:
        print('Listening for fulfilled requests...')
        while True:
            listenForFulfilledRequest()
    except KeyboardInterrupt:
        return None
