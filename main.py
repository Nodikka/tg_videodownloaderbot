import logging
from aiogram import types
from aiogram.utils.executor import start_webhook, start_polling
from aiogram.utils.exceptions import BotBlocked
from config import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import lang
from db import BotDB
import os
import yt_dlp
import requests
import instaloader
from moviepy.editor import *

WEBHOOK_HOST = 'HOST_NAME'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 8000

DB_URL = 'DATABASE_CONNECTION_URL_WITH_USERNAME_PASSWORD'
BotDB = BotDB(DB_URL)
L = instaloader.Instaloader()
class Form(StatesGroup):
    audiofile = State()
    quality = State()

async def on_startup(dispatcher):
    #await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await BotDB.connect()

async def is_supported(url):
    if 'instagram' in url:
        return 'insta'
    else:
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
            elif 'fb.watch' in url:
                return True
        return False

def download_instagram_video(link):
    post = instaloader.Post.from_shortcode(L.context, link.split('/')[-2])
    filename = f"{post.shortcode}.mp4"
    video_url = post.video_url
    with open(filename, 'wb') as f:
        f.write(requests.get(video_url).content)
    return filename

def extract_audio(video_file, audio_file):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(audio_file)
    video.close()

def download_insta_audio(link):
    post = instaloader.Post.from_shortcode(L.context, link.split('/')[-2])
    filename = f"{post.shortcode}.mp4"
    video_url = post.video_url
    with open(filename, 'wb') as f:
        f.write(requests.get(video_url).content)
    audiofile_name = f"{post.shortcode}.mp3"
    extract_audio(filename, audiofile_name)
    os.remove(filename)
    return audiofile_name
async def download_video(link):
    with yt_dlp.YoutubeDL(standart) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        afs = info_dict.get('filesize_approx')
        fs = info_dict.get('filesize')
        if afs != None and afs < 50000000:
            video_id = info_dict.get("id", None)
            video_ext = info_dict.get("ext", None)
            ydl.download(link)
            return video_id +'.' + video_ext
        elif fs != None and fs < 50000000:
            video_id = info_dict.get("id", None)
            video_ext = info_dict.get("ext", None)
            ydl.download(link)
            return video_id +'.' + video_ext
        else:
            return 'oversize'

async def download_audio(link):
    with yt_dlp.YoutubeDL(audiofile) as ydl:
        info_dict = ydl.extract_info(link)
        audio_id = info_dict.get("id", None)
        audio_ext = info_dict.get("ext", None)
        if audio_ext == 'mp3':
            return audio_id+'.'+audio_ext
        else:
            audio_ext = 'mp3'
            return audio_id+'.'+audio_ext

async def qty_download(quality, link):
    match quality:
        case '144':
            qty = low

    with yt_dlp.YoutubeDL(qty) as ydl:
        info_dict = ydl.extract_info(link)
        video_id = info_dict.get("id", None)
        video_ext = info_dict.get("ext", None)
        if video_ext != 'mp4':
            video_ext = 'mp4'
        return video_id +'.' + video_ext



def ask_markup(lang_code):
    ask_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    audio_dwn = types.KeyboardButton(lang.audiofile[lang_code])
    quality = types.KeyboardButton(lang.quality[lang_code])
    ask_markup.add(audio_dwn)
    return ask_markup
def qty_markup(lang_code):
    qty_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard= True)
    low = types.KeyboardButton('144p')
    lower = types.KeyboardButton('240p')
    medium = types.KeyboardButton('360p')
    higher = types.KeyboardButton('480p')
    high = types.KeyboardButton('720p')
    qty_markup.add(low, lower, medium, higher, high)
    return qty_markup

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    lang_markup = types.InlineKeyboardMarkup()
    uzb = types.InlineKeyboardButton('O`zbek\U0001F1FA\U0001F1FF', callback_data= 'uz')
    eng = types.InlineKeyboardButton('English\U0001F1EC\U0001F1E7', callback_data= 'eng')
    rus = types.InlineKeyboardButton('Русский\U0001F1F7\U0001F1FA', callback_data= 'ru')
    lang_markup.add(uzb, eng, rus)
    if message.from_user.language_code == 'ru':
        await message.answer('Выберите язык.', reply_markup=lang_markup)
    else: 
        await message.answer('Tilingizni tanlang.', reply_markup=lang_markup)

@dp.message_handler(commands=['savemessage'])        
@dp.message_handler(commands=['sendall'])
async def send_all_message(message: types.Message, command: Command):
    if message.from_user.id == ADMIN:
        i = 0
        if command.args:
            user_id = await BotDB.get_all_users_id()
            for id in user_id:
                try:
                    await bot.send_message(id, command.args)
                    i +=1
                except:
                    BotBlocked
            await message.answer('Done! Totals users send to: ' + str(i))


@dp.callback_query_handler(lambda call: True)
async def call_worker(query: types.CallbackQuery):
    if query.data == 'uz' :
        if await BotDB.user_exists(query.message.chat.id) == False:
            await BotDB.new_user(user_id = query.message.chat.id, lang_code = 0)
        else:
            await BotDB.save_lang_code(query.message.chat.id, 0)
        lang_code = await BotDB.get_lang_code(user_id= query.message.chat.id)
        await query.answer(lang.roger[0])
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await bot.send_message(chat_id = query.message.chat.id, text=lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
        await bot.send_message(ADMIN, 'New user/ Start command')
        
    elif query.data == 'eng':
        if await BotDB.user_exists(query.message.chat.id) == False:
            await BotDB.new_user(user_id = query.message.chat.id, lang_code = 1)
        else:
            await BotDB.save_lang_code(query.message.chat.id, 1)
        lang_code = await BotDB.get_lang_code(user_id= query.message.chat.id)
        
        await query.answer(lang.roger[1])
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await bot.send_message(chat_id = query.message.chat.id, text=lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
        await bot.send_message(ADMIN, 'New user/ Start command')
    elif query.data == 'ru':
        if await BotDB.user_exists(query.message.chat.id) == False:
            await BotDB.new_user(user_id = query.message.chat.id, lang_code = 2)
        else:
            await BotDB.save_lang_code(query.message.chat.id, 2)
        lang_code = await BotDB.get_lang_code(user_id= query.message.chat.id)
        
        await query.answer(lang.roger[2])
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        await bot.send_message(chat_id = query.message.chat.id, text=lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
        await bot.send_message(ADMIN, 'New user/ Start command')
    


@dp.message_handler(state=Form.audiofile)
async def process_audiofile_download(message: types.Message, state: FSMContext):
    lang_code = await BotDB.get_lang_code(user_id= message.chat.id)
    if await is_supported(message.text) == True:
        await message.reply(lang.downloading[lang_code])
        audio_id = await download_audio(message.text)
        if os.path.getsize(audio_id) < 50000000:
            await message.reply(lang.sending[lang_code])
            audio = open(audio_id, 'rb')
            await message.answer_audio(audio)
            audio.close()
            await message.answer(lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
            os.remove(audio_id)
            await state.finish()
            await bot.send_message(ADMIN, 'Audio Downloaded!')
        else:
            await message.reply(lang.too_big[lang_code], reply_markup=ask_markup(lang_code))
            os.remove(audio_id)
            await state.finish()
    elif await is_supported(message.text) == 'insta':
        await message.reply(lang.downloading[lang_code])
        try:
            audio_id = download_insta_audio(message.text)
        except instaloader.exceptions.ConnectionException:
            audio_id = download_audio(message.text)
        if os.path.getsize(audio_id) < 50000000:
            await message.reply(lang.sending[lang_code])
            audio = open(audio_id, 'rb')
            await message.answer_audio(audio)
            audio.close()
            await message.answer(lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
            os.remove(audio_id)
            await state.finish()
            await bot.send_message(ADMIN, 'Insta Audio Downloaded!')
        else:
            await message.reply(lang.too_big[lang_code], reply_markup=ask_markup(lang_code))
            os.remove(audio_id)
            await state.finish()
    else:
        await message.reply(lang.error_msg[lang_code], reply_markup=ask_markup(lang_code))
        await state.finish()
        await bot.send_message(ADMIN, 'URL FAILURE!!!')

@dp.message_handler(state=Form.quality)
async def process_quality_download(message: types.Message, state: FSMContext):
    lang_code = await BotDB.get_lang_code(user_id= message.chat.id)
    match message.text:
        case '144p':
            qty = '144'
            await message.answer('Link')
        case '240p':
            240
        case '360p':
            360
        case '480p':
            480
        case '720p':
            720
        case _:
            if await is_supported(message.text) == True:
                await message.reply(lang.downloading[lang_code])
                video_id = await qty_download('144', message.text)
                if os.path.getsize(video_id) < 50000000:
                    await message.reply(lang.sending[lang_code])
                    video = open(video_id, 'rb')
                    await message.answer_video(video)
                    video.close()
                    await message.answer(lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
                os.remove(video_id)
                await state.finish()
                await bot.send_message(ADMIN, 'Quality Video Downloaded!')
        
@dp.message_handler(content_types='text')
async def income_text(message: types.Message):
    lang_code = await BotDB.get_lang_code(user_id= message.chat.id)

    if message.text == lang.audiofile[lang_code]:
        await Form.audiofile.set()
        await message.reply(lang.audio_link[lang_code])
        
    elif message.text == lang.quality[lang_code] and message.chat.id == ADMIN:
        await Form.quality.set()
        await message.answer(lang.quality_link[lang_code], reply_markup=qty_markup(lang_code))    
    else:
        if await is_supported(message.text) == True:
            try:
                await message.reply(lang.downloading[lang_code])
                video_id = await download_video(message.text)
                if video_id == 'oversize':
                    await message.reply(lang.too_big[lang_code], reply_markup=ask_markup(lang_code))
                else:
                    if os.path.getsize(video_id) < 50000000:
                        await message.reply(lang.sending[lang_code])
                        video = open(video_id, 'rb')
                        await message.answer_video(video)
                        video.close()
                        await message.answer(lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
                        os.remove(video_id)
                        await bot.send_message(ADMIN, 'Video Downloaded!')
                    else:
                        await message.reply(lang.too_big[lang_code], reply_markup=ask_markup(lang_code))
                        os.remove(video_id)
            except yt_dlp.utils.DownloadError:
                await bot.send_message(chat_id=ADMIN, text="Download Error")
                await message.reply("This video is not avilable.", reply_markup=ask_markup(lang_code))
            except OSError:
                await bot.send_message(ADMIN, "No space left on device.")
                await message.reply("Error occured, Please, wait untill admin corrects this error.")
        elif await is_supported(message.text) == 'insta':
            await message.reply(lang.downloading[lang_code])
            try:
                video_id = download_instagram_video(message.text)
            except instaloader.exceptions.ConnectionException:
                try:
                    video_id = await download_video(message.text)
                except yt_dlp.utils.DownloadError:
                    await message.answer("Instagram video not avialable.")
                    video_id = "fail"
            if video_id != "fail":
                await message.reply(lang.sending[lang_code])
                video = open(video_id, 'rb')
                await message.answer_video(video)
                video.close()
                await message.answer(lang.ask_link[lang_code], reply_markup=ask_markup(lang_code))
                os.remove(video_id)
                await bot.send_message(ADMIN, 'Instagram Video Downloaded!')
        else:
            await message.reply(lang.error_msg[lang_code], reply_markup=ask_markup(lang_code))
            await bot.send_message(ADMIN, 'URL FAILURE!!!')
#yt_dlp.utils.DownloadError        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    '''start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )'''
    start_polling(dp, skip_updates=True, on_startup=on_startup)