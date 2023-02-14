import requests
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .constants import SLEEP
from .db import Database
from .utils import Config, ping

class StreamyYT:
    def __init__(self):
        self.c = Config()
        self.firefoxPath = self.c.firefoxPath
        self.youtubeApiKey = self.c.youtubeApiKey
        try:
            db = Database()
            live_channels = []
            while True:
                ping('streamy_yt')
                avatar_queue = db.getYoutubeChannelsNoAvatar()
                channels = db.getYoutubeChannels()
                if(channels == []):
                    while(channels == []):
                        time.sleep(SLEEP['streamy'])
                        channels = db.getYoutubeChannels()
                for channel in avatar_queue:
                    if not db.channelAvatarExists(channel):
                        url = self.getYoutubeProfilePictureUrl(channel)
                        if(url is None):
                            avatar_queue.remove(channel)
                            continue
                        db.updateAvatar(channel, url)
                        avatar_queue.remove(channel)
                    else:
                        avatar_queue.remove(channel)
                for channel in channels:
                    streamUrl = self.getYoutubeStreamUrl(channel)
                    print(f'{channel}: {streamUrl}')
                    if(streamUrl is None):
                        if(channel in live_channels):
                            stream_id = db.getStreamDbId(channel)
                            if stream_id is None:
                                continue
                            live_channels.remove(channel)
                            db.deleteStream(stream_id)
                    else:
                        channelDbId = db.getChannelDbId(channel)
                        if channel not in live_channels:
                            if not self.isRestrictedVideo(streamUrl):
                                live_channels.append(channel)
                                db.insertNewYoutubeStream(channelDbId, streamUrl)
                        else:
                            stream_id = db.getStreamDbId(channel)
                            currentDbUrl = db.getDbStreamUrl(stream_id)
                            if(streamUrl != currentDbUrl):
                                db.updateStream(stream_id, streamUrl)
        except KeyboardInterrupt:
            return None

    def getYoutubeStreamUrl(self, channel):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.binary_location = fr"{self.firefoxPath}"
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
    #     api_key = c.youtubeApiKey
    #     url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={self.youtubeApiKey}"
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             data = response.json()
    #             channel_id = data["items"][0]["id"]["channelId"]
    #             url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={self.youtubeApiKey}"
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
        search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={self.youtubeApiKey}'
        try:
            search_response = requests.get(search_url)
            search_data = search_response.json()
            channel_id = search_data['items'][0]['id']['channelId']
            channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={self.youtubeApiKey}'
            channel_response = requests.get(channel_url)
            channel_data = channel_response.json()
            profile_picture_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
            return profile_picture_url
        except:
            return None
        
    def isRestrictedVideo(self, url):
        return True if len(url.split('&amp')) > 1 else False