import requests
import time

import mysql.connector

from .utils import Config

c = Config()
CLIENT_ID = c.twitchClientId
SECRET_KEY = c.twitchSecretKey

def getHeaders():
    return {"Authorization": f"Bearer {getOAuth(CLIENT_ID, SECRET_KEY)}",
            "Client-Id": CLIENT_ID}

def getOAuth(client_id, client_secret):
    try:
        response = requests.post(
            f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
        )
        return response.json()['access_token']
    except:
        return None

def getTwitchChannels():
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = 'SELECT url FROM channels WHERE type = "Twitch";'
    cursor.execute(sql)
    urls = cursor.fetchall()
    channels = []
    for url in urls:
        channels.append(url[0].split('.tv/')[1])
    cursor.close()
    db.close()
    return channels

def isTwitchStreamLive(channel):
    url = f'https://api.twitch.tv/helix/streams?user_login={channel}'
    try:
        resp = requests.get(url,params=None,headers=getHeaders()).json()
        return resp['data'] != []
    except:
        return False

def getChannelDbId(channel):
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'SELECT id FROM channels WHERE name = "{channel}";'
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return id

def getStreamDbId(channel):
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'SELECT s.id FROM streams s INNER JOIN channels c ON s.channel_id=c.id WHERE c.name="{channel}";'
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return id

def isStreamActive(channel_id):
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'SELECT live FROM streams WHERE channel_id={channel_id} ORDER BY id DESC LIMIT 1;'
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result is None:
        return False
    else:
        return result[0] == 1
    
def insertNewStream(channel, channelDbId):
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"https://twitch.tv/{channel}",1);'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def deleteStream(stream_id):
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'DELETE FROM streams WHERE id={stream_id};'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def deleteStreams():
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="streamy"
            )
    cursor = db.cursor()
    sql = f'DELETE FROM streams;'
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

live_channels = []
stream_id = 0

def run():
    try:
        print('Streamy is running. Updating streams...')
        while True:
            twitch_channels = getTwitchChannels()
            for channel in twitch_channels:
                if(isTwitchStreamLive(channel)):
                    try:
                        channelDbId = getChannelDbId(channel)
                    except:
                        continue
                    if not isStreamActive(channelDbId):
                        insertNewStream(channel, channelDbId)
                        if channel not in live_channels:
                            live_channels.append(channel)
                    else:
                        if channel not in live_channels:
                            live_channels.append(channel)
                else:
                    if(channel in live_channels):
                        live_channels.remove(channel)
                        stream_id = getStreamDbId(channel)
                        deleteStream(stream_id)
            time.sleep(3)
    except KeyboardInterrupt:
        return None