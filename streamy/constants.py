import os

import pyfiglet

CONFIG_FILE = 'streamy.ini'
BANNER = f'\033[0;92m{pyfiglet.figlet_format("Streamy", font="smkeyboard")}\033[0m'
INTRO = 'splash.mp4'
if(os.name == 'nt'):
    MPV = 'mpv.exe'
else:
    MPV = 'mpv'
MONITOR = 1
SLEEP = {'listener_end':5,
         'listener_requests':3,
         'streamy':1}