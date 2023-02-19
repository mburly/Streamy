import psutil
import requests
import subprocess
from threading import Thread
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .constants import INTRO, MPV, MONITOR, SLEEP
from .db import Database
from .utils import Config, ping

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
                            self.streamId = self.db.getStreamDbId(channel)
                            self.db.deleteStream(self.streamId)
                time.sleep(SLEEP['streamy'])
        except KeyboardInterrupt:
            return None

    def getHeaders(self):
        return {"Authorization": f"Bearer {self.getOAuth(self.c.twitchClientId, self.c.twitchSecretKey)}",
                "Client-Id": self.c.twitchClientId}

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
        
class StreamyYT:
    def __init__(self):
        try:
            self.c = Config()
            self.db = Database()
            self.live_channels = []
            while True:
                ping('streamy_yt')
                self.avatar_queue = self.db.getYoutubeChannelsNoAvatar()
                self.channels = self.db.getYoutubeChannels()
                if(self.channels == []):
                    while(self.channels == []):
                        time.sleep(SLEEP['streamy'])
                        self.channels = self.db.getYoutubeChannels()
                for channel in self.avatar_queue:
                    if not self.db.channelAvatarExists(channel):
                        url = self.getYoutubeProfilePictureUrl(channel)
                        if(url is None):
                            self.avatar_queue.remove(channel)
                            continue
                        self.db.updateAvatar(channel, url)
                        self.avatar_queue.remove(channel)
                    else:
                        self.avatar_queue.remove(channel)
                for channel in self.channels:
                    streamUrl = self.getYoutubeStreamUrl(channel)
                    print(f'{channel}: {streamUrl}')
                    if(streamUrl is None):
                        if(channel in self.live_channels):
                            streamId = self.db.getStreamDbId(channel)
                            if streamId is None:
                                continue
                            self.live_channels.remove(channel)
                            self.db.deleteStream(streamId)
                    else:
                        channelDbId = self.db.getChannelDbId(channel)
                        if channel not in self.live_channels:
                            if not self.isRestrictedVideo(streamUrl):
                                self.live_channels.append(channel)
                                self.db.insertNewYoutubeStream(channelDbId, streamUrl)
                        else:
                            streamId = self.db.getStreamDbId(channel)
                            currentDbUrl = self.db.getDbStreamUrl(streamId)
                            if(streamUrl != currentDbUrl):
                                if not self.isRestrictedVideo(streamUrl):
                                    self.db.updateStream(streamId, streamUrl)
                                else:
                                    self.db.deleteStream(streamId)
        except KeyboardInterrupt:
            return None

    def getYoutubeStreamUrl(self, channel):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.binary_location = fr"{self.c.firefoxPath}"
        url = f'https://www.youtube.com/@{channel}'
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        time.sleep(SLEEP['streamy'])
        htmlSource = driver.page_source
        driver.quit()
        if(len(htmlSource.split('aria-label="LIVE"')) > 1):
            streamUrl = htmlSource.split('inline-block style-scope ytd-thumbnail" aria-hidden="true" tabindex="-1" rel="null" href="')[1].split('">')[0]
            streamUrl = f'https://www.youtube.com{streamUrl}'
            return streamUrl
        else:
            return None
        
    # def getYoutubeStreamUrl(self, channel_name):
    #     url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={self.c.youtubeApiKey}"
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             data = response.json()
    #             channel_id = data["items"][0]["id"]["channelId"]
    #             url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={self.c.youtubeApiKey}"
    #             response = requests.get(url)
    #             if response.status_code == 200:
    #                 data = response.json()
    #                 for item in data["items"]:
    #                     video_id = item["id"]["videoId"]
    #                     video_url = f"https://www.youtube.com/watch?v={video_id}"
    #                     return video_url
    #             else:
    #                 return None
    #     except:
    #         return None

    def getYoutubeProfilePictureUrl(self, channel_name):
        search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={self.c.youtubeApiKey}'
        try:
            search_response = requests.get(search_url)
            search_data = search_response.json()
            channel_id = search_data['items'][0]['id']['channelId']
            channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={self.c.youtubeApiKey}'
            channel_response = requests.get(channel_url)
            channel_data = channel_response.json()
            profile_picture_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
            return profile_picture_url
        except:
            return None
        
    def isRestrictedVideo(self, url):
        return True if len(url.split('&amp')) > 1 else False
    
class ListenerEnd:
    def __init__(self):
        try:
            self.db = Database()
            while True:
                ping('listener_end')
                self.listenForFulfilledRequest()
        except KeyboardInterrupt:
            return None

    def listenForFulfilledRequest(self):
        stream_running = True
        while(stream_running):
            try:
                if(self.db.isRequestFulfilled()):
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
                    streamId = self.db.getLastRequestStreamId()
                    url = self.db.getLastRequestUrl(streamId)
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