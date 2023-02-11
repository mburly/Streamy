import requests
import time

import mysql.connector
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .utils import Config

c = Config()
API_KEY = c.youtubeApiKey

def deleteStream(stream_id):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = f'DELETE FROM streams WHERE id={stream_id};'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def getStreamDbId(channel):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = f'SELECT s.id FROM streams s INNER JOIN channels c ON s.channel_id=c.id WHERE c.name="{channel}";'
    cursor.execute(sql)
    try:
        id = cursor.fetchone()[0]
    except:
        return None
    cursor.close()
    db.close()
    return id

def getYoutubeStreamUrl(channel):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.binary_location = fr"{c.firefoxPath}"
    url = f'https://www.youtube.com/@{channel}'
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(1)
    htmlSource = driver.page_source
    driver.quit()
    if(len(htmlSource.split('aria-label="LIVE"')) > 1):
        streamUrl = htmlSource.split('inline-block style-scope ytd-thumbnail" aria-hidden="true" tabindex="-1" rel="null" href="')[1].split('">')[0]
        streamUrl = f'https://www.youtube.com{streamUrl}'
        return streamUrl
    else:
        return None
    
# def getYoutubeStreamUrl(channel_name):
#     api_key = c.youtubeApiKey
#     url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={api_key}"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             channel_id = data["items"][0]["id"]["channelId"]
#             url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={api_key}"
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
    
def getYoutubeChannels():
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = 'SELECT url FROM channels WHERE type = "Youtube";'
    cursor.execute(sql)
    urls = cursor.fetchall()
    channels = []
    for url in urls:
        channels.append(url[0].split('.com/@')[1])
    cursor.close()
    db.close()
    return channels

def getYoutubeChannelsNoAvatar():
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = 'SELECT name FROM channels WHERE avatar_url = " " OR avatar_url IS NULL;'
    cursor.execute(sql)
    names = cursor.fetchall()
    channels = []
    for name in names:
        channels.append(name[0])
    cursor.close()
    db.close()
    return channels

def getChannelDbId(channel):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = f'SELECT id FROM channels WHERE name = "{channel}";'
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return id

def updateAvatar(channel, url):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    id = getChannelDbId(channel)
    sql = f'UPDATE channels SET avatar_url = "{url}" WHERE id={id};'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def insertNewStream(channelDbId, streamUrl):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"{streamUrl}",1);'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def channelAvatarExists(channel):
    db = mysql.connector.connect(
                host=c.dbHost,
                user=c.dbUser,
                password=c.dbPassword,
                database=c.dbName
            )
    cursor = db.cursor()
    sql = f'SELECT avatar_url FROM channels WHERE name = "{channel}";'
    cursor.execute(sql)
    val = cursor.fetchone()[0]
    cursor.close()
    db.close()
    if val is None or val == '':
        return False
    return True

def getYoutubeProfilePictureUrl(channel_name):
    search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={API_KEY}'
    try:
        search_response = requests.get(search_url)
        search_data = search_response.json()
        channel_id = search_data['items'][0]['id']['channelId']
        channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={API_KEY}'
        channel_response = requests.get(channel_url)
        channel_data = channel_response.json()
        profile_picture_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
        return profile_picture_url
    except:
        return None

def run():
    try:
        live_channels = []
        print('Listening for YouTube streams...')
        while True:
            print('[PING] streamy_yt.py')
            avatar_queue = getYoutubeChannelsNoAvatar()
            channels = getYoutubeChannels()
            if(channels == []):
                while(channels == []):
                    time.sleep(1)
                    channels = getYoutubeChannels()
            for channel in avatar_queue:
                if not channelAvatarExists(channel):
                    url = getYoutubeProfilePictureUrl(channel)
                    if(url is None):
                        avatar_queue.remove(channel)
                        continue
                    updateAvatar(channel, url)
                    avatar_queue.remove(channel)
                else:
                    avatar_queue.remove(channel)
            for channel in channels:
                streamUrl = getYoutubeStreamUrl(channel)
                print(f'{channel}: {streamUrl}')
                if(streamUrl is None):
                    if(channel in live_channels):
                        stream_id = getStreamDbId(channel)
                        if stream_id is None:
                            continue
                        live_channels.remove(channel)
                        deleteStream(stream_id)
                else:
                    if channel not in live_channels:
                        live_channels.append(channel)
                        channelDbId = getChannelDbId(channel)
                        insertNewStream(channelDbId, streamUrl)
            # time.sleep(60)
    except KeyboardInterrupt:
        return None