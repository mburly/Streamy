import requests
import time

from .constants import SLEEP
from .db import Database
from .utils import Config, ping

c = Config()

class Streamy:
    def __init__(self):
        try:
            db = Database()
            live_channels = []
            stream_id = 0
            while True:
                ping('streamy')
                twitch_channels = db.getTwitchChannels()
                for channel in twitch_channels:
                    if(self.isTwitchStreamLive(channel)):
                        try:
                            channelDbId = db.getChannelDbId(channel)
                        except:
                            continue
                        if not db.isStreamActive(channelDbId):
                            db.insertNewTwitchStream(channel, channelDbId)
                            if channel not in live_channels:
                                live_channels.append(channel)
                        else:
                            if channel not in live_channels:
                                live_channels.append(channel)
                    else:
                        if(channel in live_channels):
                            live_channels.remove(channel)
                            stream_id = db.getStreamDbId(channel)
                            db.deleteStream(stream_id)
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