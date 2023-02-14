import subprocess
import time
from threading import Thread

from .constants import MPV
from .db import Database

SLEEP_TIME = 3
MONITOR = 1

def playTwitchStream(stream):
    time.sleep(SLEEP_TIME)
    try:
        subprocess.run(["streamlink", "-p", MPV, "-a", f"\"-fs-screen={MONITOR}\"", stream, "best", "--twitch-low-latency"])
    except:
        return None

def playYoutubeStream(stream):
    time.sleep(SLEEP_TIME)
    try:
        subprocess.run(["streamlink", "-p", MPV, "-a", f"\"-fs-screen={MONITOR}\"", stream, "best"])
    except:
        return None

def playIntro():
    subprocess.run(["mpv", "--fs", f"-fs-screen={MONITOR}", "--loop=no", 'streamy-intro.mp4'])


def run():
    try:
        db = Database()
        prevId = db.getLastRequestId()
        print('Listening for requests...')
        while True:
            print('[PING] listener_requests.py')
            try:
                id = db.getLastRequestId()
            except:
                id = db.getLastRequestId()
            if(prevId != id):
                stream_id = db.getLastRequestStreamId()
                url = db.getLastRequestUrl(stream_id)
                if(db.getLastRequestChannelType() == "Youtube"):
                    Thread(target = playIntro).start()
                    Thread(target = playYoutubeStream(url)).start()
                else:
                    Thread(target = playIntro).start()
                    Thread(target = playTwitchStream(url)).start()
            prevId = id
            time.sleep(3)
    except KeyboardInterrupt:
        return None
