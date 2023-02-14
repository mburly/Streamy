import psutil
import time

from .constants import MPV
from .db import Database

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
        if proc.name() == MPV:
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
