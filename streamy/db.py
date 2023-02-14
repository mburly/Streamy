import mysql.connector

from .utils import Config

class Database:
    def __init__(self):
        self.c = Config()
    
    def connect(self):
        db = mysql.connector.connect(
                host=self.c.dbHost,
                user=self.c.dbUser,
                password=self.c.dbPassword,
                database=self.c.dbName
            )
        return db
    
    def channelAvatarExists(self, channel):
        db = self.connect()
        cursor = db.cursor()
        sql = f'SELECT avatar_url FROM channels WHERE name = "{channel}";'
        cursor.execute(sql)
        val = cursor.fetchone()[0]
        cursor.close()
        db.close()
        if val is None or val == '':
            return False
        return True
    
    def deleteStream(self, stream_id):
        db = self.connect()
        cursor = db.cursor()
        sql = f'DELETE FROM streams WHERE id={stream_id};'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    def deleteStreams(self):
        db = self.connect()
        cursor = db.cursor()
        sql = f'DELETE FROM streams;'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    def getChannelDbId(self, channel):
        db = self.connect()
        cursor = db.cursor()
        sql = f'SELECT id FROM channels WHERE name = "{channel}";'
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return id

    def getDbStreamUrl(self, stream_id):
        db = self.connect()
        cursor = db.cursor()
        sql = f'SELECT url FROM streams WHERE id={stream_id};'
        cursor.execute(sql)
        url = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return url
    
    def getLastRequestChannelType(self):
        db = self.connect()
        cursor = db.cursor()
        sql = f'SELECT c.type FROM channels c INNER JOIN streams s ON c.id = s.channel_id INNER JOIN requests r ON s.id = r.stream_id ORDER BY r.id DESC LIMIT 1;'
        cursor.execute(sql)
        type = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return type

    def getLastRequestId(self):
        db = self.connect()
        cursor = db.cursor()
        sql = 'SELECT MAX(id) FROM requests;'
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return id

    def getLastRequestStreamId(self):
        db = self.connect()
        cursor = db.cursor()
        sql = 'SELECT stream_id FROM requests ORDER BY id DESC LIMIT 1;'
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return id

    def getLastRequestUrl(self, stream_id):
        db = self.connect()
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
    
    def getStreamDbId(self, channel):
        db = self.connect()
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
    
    def getTwitchChannels(self):
        db = self.connect()
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

    def getYoutubeChannels(self):
        db = self.connect()
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
    
    def getYoutubeChannelsNoAvatar(self):
        db = self.connect()
        cursor = db.cursor()
        sql = 'SELECT name FROM channels WHERE avatar_url = " " OR avatar_url IS NULL;'
        cursor.execute(sql)
        names = cursor.fetchall()
        channels = []
        for name in names:
            if(name[0] == ''):
                continue
            channels.append(name[0])
        cursor.close()
        db.close()
        return channels
    
    def insertNewTwitchStream(self, channel, channelDbId):
        db = self.connect()
        cursor = db.cursor()
        sql = f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"https://twitch.tv/{channel}",1);'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
    
    def insertNewYoutubeStream(self, channelDbId, streamUrl):
        db = self.connect()
        cursor = db.cursor()
        sql = f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"{streamUrl}",1);'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    def isRequestFulfilled(self):
        db = self.connect()
        cursor = db.cursor()
        sql = f'SELECT done FROM requests ORDER BY id DESC LIMIT 1;'
        cursor.execute(sql)
        try:
            done = cursor.fetchone()[0]
        except:
            return True
        cursor.close()
        db.close()
        if done is None:
            return False
        return True if done == 1 else False
    
    def isStreamActive(self, channel_id):
        db = self.connect()
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

    def updateStream(self, stream_id, url):
        db = self.connect()
        cursor = db.cursor()
        sql = f'UPDATE streams SET url = "{url}" WHERE id={stream_id};'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    def updateAvatar(self, channel, url):
        db = self.connect()
        cursor = db.cursor()
        id = self.getChannelDbId(channel)
        sql = f'UPDATE channels SET avatar_url = "{url}" WHERE id={id};'
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
