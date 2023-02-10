import configparser

CONFIG_FILE = 'streamy.ini'

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)
        self.twitchClientId = self.config['Twitch']['client_id']
        self.twitchSecretKey = self.config['Twitch']['client_secret']
        self.youtubeApiKey = self.config['Youtube']['api_key']
        self.dbHost = self.config['Db']['host']
        self.dbUser = self.config['Db']['user']
        self.dbPassword = self.config['Db']['password']
        self.firefoxPath = self.config['Firefox']['path']
        self.dbName = 'streamy'