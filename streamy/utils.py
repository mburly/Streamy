import os

import configparser

from .constants import BANNER, CONFIG_FILE

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

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def ping(module):
    print(f'[PING] {module}')

def printBanner():
    os.system("")
    cls()
    print(BANNER)