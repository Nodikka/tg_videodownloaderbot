import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = 'BOT_TOKEN'
ADMIN = 'ADMIN_ID'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())




standart= {
    'cookiefile': 'cookies.txt',
    'xff': 'UZ',
    'format': 'mp4[filesize<40M][height<=720][width<=1080]/mp4[filesize<50M][height<=720][width<=1080]/mp4[filesize<100M]/mp4[filesize<250M]/best',
    'outtmpl': '%(id)s.%(ext)s',
    'playlist_items': '1'
}
audiofile = {
    'cookiefile': 'cookies.txt',
    'xff': 'UZ',
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'playlist_items': '1',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
#