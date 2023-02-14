import os
import psutil
import time

from .db import Database

if(os.name == 'nt'):
    PROC_NAME = "mpv.exe"
else:
    PROC_NAME = "mpv"


def listenForFulfilledRequest():
    db = Database()
    stream_running = True
    while(stream_running):
        try:
            if(db.isRequestFulfilled()):
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
