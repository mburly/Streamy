import subprocess
import time
from threading import Thread

from .constants import MPV, MONITOR, SLEEP
from .db import Database
from .utils import ping

class ListenerRequests:
    def __init__(self):
        try:
            db = Database()
            prevId = db.getLastRequestId()
            while True:
                ping('listener_requests')
                try:
                    id = db.getLastRequestId()
                except:
                    id = db.getLastRequestId()
                if(prevId != id):
                    stream_id = db.getLastRequestStreamId()
                    url = db.getLastRequestUrl(stream_id)
                    if(db.getLastRequestChannelType() == "Youtube"):
                        Thread(target = self.playIntro).start()
                        Thread(target = self.playYoutubeStream(url)).start()
                    else:
                        Thread(target = self.playIntro).start()
                        Thread(target = self.playTwitchStream(url)).start()
                prevId = id
                time.sleep(SLEEP['listener_requests'])
        except KeyboardInterrupt:
            return None

    def playTwitchStream(self, stream):
        time.sleep(SLEEP['listener_requests'])
        try:
            subprocess.run(["streamlink", "-p", MPV, "-a", f"\"-fs-screen={MONITOR}\"", stream, "best", "--twitch-low-latency"])
        except:
            return None

    def playYoutubeStream(self, stream):
        time.sleep(SLEEP['listener_requests'])
        try:
            subprocess.run(["streamlink", "-p", MPV, "-a", f"\"-fs-screen={MONITOR}\"", stream, "best"])
        except:
            return None
        
    def playIntro(self):
        subprocess.run(["mpv", "--fs", f"-fs-screen={MONITOR}", "--loop=no", 'streamy-intro.mp4'])
