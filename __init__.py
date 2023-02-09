import os
import time
from threading import Event, Thread

import pyfiglet

from streamy import streamy, streamy_yt, listener_requests, listener_end

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

if __name__ == '__main__':
    os.system("")
    cls()
    banner = pyfiglet.figlet_format('Streamy', font="smkeyboard")
    print(f'\033[0;92m{banner}\033[0m')
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
        streamy.deleteStreams()
        if(os.name == 'nt'):
            os._exit(0)
        else:
            os.kill(os.getpid(), signal.SIGINT)
