import psutil
import time

from .constants import MPV, SLEEP
from .db import Database
from .utils import ping

class ListenerEnd:
    def __init__(self):
        try:
            while True:
                ping('listener_end')
                self.listenForFulfilledRequest()
        except KeyboardInterrupt:
            return None

    def listenForFulfilledRequest(self):
        db = Database()
        stream_running = True
        while(stream_running):
            try:
                if(db.isRequestFulfilled()):
                    self.killMpv()
                    stream_running = False
            except:
                return None
            time.sleep(SLEEP['listener_end'])

    def killMpv(self):
        for proc in psutil.process_iter():
            if proc.name() == MPV:
                try:
                    proc.kill()
                except:
                    return None