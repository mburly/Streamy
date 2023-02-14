import requests
import time

from .constants import SLEEP
from .db import Database
from .utils import Config, ping

c = Config()

class Streamy:
    def __init__(self):
        try:
            self.c = Config()
            self.db = Database()
            self.live_channels = []
            while True:
                ping('streamy')
                twitch_channels = self.db.getTwitchChannels()
                for channel in twitch_channels:
                    if(self.isTwitchStreamLive(channel)):
                        try:
                            channelDbId = self.db.getChannelDbId(channel)
                        except:
                            continue
                        if not self.db.isStreamActive(channelDbId):
                            self.db.insertNewTwitchStream(channel, channelDbId)
                            if channel not in self.live_channels:
                                self.live_channels.append(channel)
                        else:
                            if channel not in self.live_channels:
                                self.live_channels.append(channel)
                    else:
                        if(channel in self.live_channels):
                            self.live_channels.remove(channel)
                            self.stream_id = self.db.getStreamDbId(channel)
                            self.db.deleteStream(self.stream_id)
                time.sleep(SLEEP['streamy'])
        except KeyboardInterrupt:
            return None

    def getHeaders(self):
        return {"Authorization": f"Bearer {self.getOAuth(c.twitchClientId, c.twitchSecretKey)}",
                "Client-Id": c.twitchClientId}

    def getOAuth(self, client_id, client_secret):
        try:
            response = requests.post(
                f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
            )
            return response.json()['access_token']
        except:
            return None

    def isTwitchStreamLive(self, channel):
        url = f'https://api.twitch.tv/helix/streams?user_login={channel}'
        try:
            resp = requests.get(url,params=None,headers=self.getHeaders()).json()
            return resp['data'] != []
        except:
            return False