import os
import time
from threading import Event, Thread

from streamy import streamy, streamy_yt, listener_requests, listener_end
from streamy.db import Database
from streamy.utils import printBanner

if __name__ == '__main__':
    printBanner()
    db = Database()
    db.verify()
    run_event = Event()
    run_event.set()
    t1 = Thread(target = streamy_yt.run)
    t2 = Thread(target = streamy.run)
    t3 = Thread(target = listener_requests.run)
    t4 = Thread(target = listener_end.run)
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
