import subprocess
import time
from threading import Thread

from .constants import INTRO, MPV, MONITOR, SLEEP
from .db import Database
from .utils import ping

class ListenerRequests:
    def __init__(self):
        try:
            self.db = Database()
            self.prevId = self.db.getLastRequestId()
            while True:
                ping('listener_requests')
                try:
                    id = self.db.getLastRequestId()
                except:
                    id = self.db.getLastRequestId()
                if(self.prevId != id):
                    stream_id = self.db.getLastRequestStreamId()
                    url = self.db.getLastRequestUrl(stream_id)
                    if(self.db.getLastRequestChannelType() == "Youtube"):
                        Thread(target = self.playIntro).start()
                        Thread(target = self.playYoutubeStream(url)).start()
                    else:
                        Thread(target = self.playIntro).start()
                        Thread(target = self.playTwitchStream(url)).start()
                self.prevId = id
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
        subprocess.run(["mpv", "--fs", f"-fs-screen={MONITOR}", "--loop=no", INTRO])
