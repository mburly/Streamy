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
    
    def commit(self, sql):
        db = self.connect()
        cursor = db.cursor()
        if(type(sql) == list):
            for stmt in sql:
                cursor.execute(stmt)
            db.commit()
        else:
            cursor.execute(sql)
            db.commit()
        cursor.close()
        db.close()

    def get(self, sql):
        db = self.connect()
        cursor = db.cursor()
        cursor.execute(sql)
        try:
            val = cursor.fetchone()[0]
        except:
            return None
        cursor.close()
        db.close()
        return val
    
    def getMany(self, sql):
        db = self.connect()
        cursor = db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        vals = []
        if(sql == stmtSelectTwitchChannels()):
            for result in results:
                vals.append(result[0].split('.tv/')[1])
        elif(sql == stmtSelectYoutubeChannels()):
            for result in results:
                vals.append(result[0].split('.com/@')[1])
        elif(sql == stmtSelectYoutubeChannelsNoAvatar()):
            for result in results:
                if(result[0] == ''):
                    continue
                vals.append(result[0])
        cursor.close()
        db.close()
        return vals
    
    def channelAvatarExists(self, channel):
        url = self.get(f'SELECT avatar_url FROM channels WHERE name = "{channel}";')
        if url is None or url == '':
            return False
        return True
    
    def deleteStream(self, stream_id):
        self.commit(f'DELETE FROM streams WHERE id={stream_id};')

    def deleteStreams(self):
        self.commit('DELETE FROM streams;')

    def getChannelDbId(self, channel):
        return self.get(f'SELECT id FROM channels WHERE name = "{channel}";')

    def getDbStreamUrl(self, stream_id):
        return self.get(f'SELECT url FROM streams WHERE id={stream_id};')
    
    def getLastRequestChannelType(self):
        return self.get(f'SELECT c.type FROM channels c INNER JOIN streams s ON c.id = s.channel_id INNER JOIN requests r ON s.id = r.stream_id ORDER BY r.id DESC LIMIT 1;')

    def getLastRequestId(self):
        return self.get('SELECT MAX(id) FROM requests;')

    def getLastRequestStreamId(self):
        return self.get('SELECT stream_id FROM requests ORDER BY id DESC LIMIT 1;')

    def getLastRequestUrl(self, stream_id):
        return self.get(f'SELECT s.url FROM streams s INNER JOIN requests r ON s.id=r.stream_id WHERE s.id={stream_id} LIMIT 1;')
    
    def getStreamDbId(self, channel):
        return self.get(f'SELECT s.id FROM streams s INNER JOIN channels c ON s.channel_id=c.id WHERE c.name="{channel}";')
    
    def getTwitchChannels(self):
        return self.getMany(stmtSelectTwitchChannels())

    def getYoutubeChannels(self):
        return self.getMany(stmtSelectYoutubeChannels())
    
    def getYoutubeChannelsNoAvatar(self):
        return self.getMany(stmtSelectYoutubeChannelsNoAvatar())
    
    def insertNewTwitchStream(self, channel, channelDbId):
        self.commit(f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"https://twitch.tv/{channel}",1);')
    
    def insertNewYoutubeStream(self, channelDbId, streamUrl):
        self.commit(f'INSERT INTO streams (channel_id, url, live) VALUES ({channelDbId},"{streamUrl}",1);')

    def isRequestFulfilled(self):
        done = self.get('SELECT done FROM requests ORDER BY id DESC LIMIT 1;')
        if done is None:
            return False
        return done == 1
    
    def isStreamActive(self, channel_id):
        live = self.get(f'SELECT live FROM streams WHERE channel_id={channel_id} ORDER BY id DESC LIMIT 1;')
        if live is None:
            return False
        else:
            return live == 1

    def updateStream(self, stream_id, url):
        self.commit(f'UPDATE streams SET url = "{url}" WHERE id={stream_id};')

    def updateAvatar(self, channel, url):
        id = self.getChannelDbId(channel)
        self.commit(f'UPDATE channels SET avatar_url = "{url}" WHERE id={id};')


def stmtSelectTwitchChannels():
    return 'SELECT url FROM channels WHERE type = "Twitch";'

def stmtSelectYoutubeChannels():
    return 'SELECT url FROM channels WHERE type = "Youtube";'

def stmtSelectYoutubeChannelsNoAvatar():
    return 'SELECT name FROM channels WHERE avatar_url = " " OR avatar_url IS NULL;'