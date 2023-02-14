import os
import time
from threading import Event, Thread

from streamy.db import Database
from streamy.streamy import ListenerEnd, ListenerRequests, Streamy, StreamyYT
from streamy.utils import printBanner

if __name__ == '__main__':
    printBanner()
    db = Database()
    db.verify()
    run_event = Event()
    run_event.set()
    t1 = Thread(target=StreamyYT)
    t2 = Thread(target=Streamy)
    t3 = Thread(target=ListenerRequests)
    t4 = Thread(target=ListenerEnd)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        db.deleteStreams()
        if(os.name == 'nt'):
            os._exit(0)
        else:
            os.kill(os.getpid(), signal.SIGINT)
