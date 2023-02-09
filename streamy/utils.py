import configparser

CONFIG_FILE = 'streamy.ini'

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)
        self.twitchClientId = self.config['Twitch']['client_id']
        self.twitchSecretKey = self.config['Twitch']['client_secret']
        self.youtubeApiKey = self.config['Youtube']['api_key']