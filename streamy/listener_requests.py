import subprocess
import time
from threading import Thread

import mysql.connector

from .utils import Config

c = Config()
SLEEP_TIME = 3
MONITOR = 1

def playTwitchStream(stream):
    time.sleep(SLEEP_TIME)
    try:
        subprocess.run(["streamlink", "-p", "mpv.exe", "-a", f"\"-fs-screen={MONITOR}\"", stream, "best", "--twitch-low-latency"])
    except:
        return None

def playYoutubeStream(stream):
    time.sleep(SLEEP_TIME)
    try:
        subprocess.run(["streamlink", "-p", "mpv.exe", "-a", f"\"-fs-screen={MONITOR}\"", stream, "best"])
    except:
        return None

def playIntro():
    subprocess.run(["mpv", "--fs", f"-fs-screen={MONITOR}", "--loop=no", 'streamy-intro.mp4'])

def getLastRequestId():
    db = mysql.connector.connect(
            host=c.dbHost,
            user=c.dbUser,
            password=c.dbPassword,
            database=c.dbName
        )
    cursor = db.cursor()
    sql = 'SELECT MAX(id) FROM requests;'
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return id

def getLastRequestStreamId():
    db = mysql.connector.connect(
            host=c.dbHost,
            user=c.dbUser,
            password=c.dbPassword,
            database=c.dbName
        )
    cursor = db.cursor()
    sql = 'SELECT stream_id FROM requests ORDER BY id DESC LIMIT 1;'
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return id

def getLastRequestUrl(stream_id):
    db = mysql.connector.connect(
            host=c.dbHost,
            user=c.dbUser,
            password=c.dbPassword,
            database=c.dbName
        )
    cursor = db.cursor()
    sql = f'SELECT s.url FROM streams s INNER JOIN requests r ON s.id=r.stream_id WHERE s.id={stream_id} LIMIT 1;'
    cursor.execute(sql)
    try:
        url = cursor.fetchone()[0]
    except:
        return None
    cursor.close()
    db.close()
    return url

def getLastRequestChannelType():
    db = mysql.connector.connect(
            host=c.dbHost,
            user=c.dbUser,
            password=c.dbPassword,
            database=c.dbName
        )
    cursor = db.cursor()
    sql = f'SELECT c.type FROM channels c INNER JOIN streams s ON c.id = s.channel_id INNER JOIN requests r ON s.id = r.stream_id ORDER BY r.id DESC LIMIT 1;'
    cursor.execute(sql)
    type = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return type

def run():
    try:
        prevId = getLastRequestId()
        print('Listening for requests...')
        while True:
            print('[PING] listener_requests.py')
            try:
                id = getLastRequestId()
            except:
                id = getLastRequestId()
            if(prevId != id):
                stream_id = getLastRequestStreamId()
                url = getLastRequestUrl(stream_id)
                if(getLastRequestChannelType() == "Youtube"):
                    Thread(target = playIntro).start()
                    Thread(target = playYoutubeStream(url)).start()
                else:
                    Thread(target = playIntro).start()
                    Thread(target = playTwitchStream(url)).start()
            prevId = id
            time.sleep(3)
    except KeyboardInterrupt:
        return None
