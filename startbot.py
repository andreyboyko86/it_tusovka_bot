from ast import Lambda
from aiogram import Bot, Dispatcher,types
from aiogram.utils import executor
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import tweepy
import json
import re
from config import settings
from FromTwitter import TwitterMedia
import datetime as DT
import asyncio

#Константы

CHAT_BY_DATETIME = dict()

# Работа с твиттером


def getNews(twitterName):
    consumer_key = settings['consumer_key']
    consumer_secret = settings['consumer_secret']
    access_token = settings['access_token']
    access_token_secret = settings['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    items = []
    Tweet = []
    search_words  = '#UkraineRussianWar'      #enter your words
    search_words2 = '#Ukrainewar'
    api = tweepy.API(auth, proxy='')
    tweets_list= api.user_timeline(screen_name=twitterName, count=10,tweet_mode="extended",include_rts=False) # Get the last tweet

    tweet= tweets_list
    for element in tweet:
        if str(element.full_text).find(search_words) ==0 or str(element.full_text).find(search_words2) ==0:
            media = element.entities.get('media', [])
            urls = element.entities.get('hashtags', [])
            if(len(media) > 0) or (len(urls)>0):  
                try:
                    url_media = media[0]['media_url']
                    if str(element.full_text) not in items:
                            Tweet.append({
                                        "date"  : element.created_at,
                                        "tweet" : re.sub(r'(," ")(?=$)',r'',re.sub(r"https?://[^,\s]+,?", "", element.full_text)),
                                         "url"   : url_media
                                        }) 
                            items.append(str(element.full_text))
                except:
                   if str(element.full_text) not in items:
                        Tweet.append({
                                    "date"  : element.created_at,
                                    "tweet" : re.sub(r'(," ")(?=$)',r'',re.sub(r"https?://[^,\s]+,?", "", element.full_text)),
                                    }) 
                        items.append(str(element.full_text))
    with open('tweets.json','w',encoding='utf-8') as file:
        json.dump(Tweet,file,indent=4,ensure_ascii=False,default=str)

downloader = TwitterMedia()

# Область бота

TOKEN    = settings['TOKEN']
bot  = Bot(token = TOKEN, parse_mode=types.ParseMode.HTML) # Создаем бота
dp = Dispatcher(bot)

async def on_startup(_):
    print('Бот онлайн')

# Создаем кнопки бота

InlKB = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Узнать обстановку на фронте',callback_data='News'))

# Хендлеры бота

@dp.message_handler(commands=['start','help'])
async def command_start(message : types.Message):
   
        
    await bot.send_message(message.chat.id,'Бот запущен! Пацаны не спят, пацаны мониторят обстановку на фронте',reply_markup=InlKB)

@dp.message_handler()
async def bot_message(message: types.Message):
    t ='https://twitter.com'
    if t in message.text:
        tweet = downloader.fetch_media(message.text)
        if hasattr(tweet,'url'):
            url   = tweet.url
            await bot.delete_message(message.chat.id,message.message_id) # Удаляем исходную ссылку
            await bot.send_message(message.chat.id,url)
        else:
            await bot.send_message(message.chat.id,message.text)

@dp.callback_query_handler(text='News')
async def get_news(callback : types.CallbackQuery):
   
    need_seconds = 50
    current_time = DT.datetime.now()
    last_datetime = CHAT_BY_DATETIME.get(callback.message.chat.id)
    text ='^'

    # Если первое сообщение (время не задано)
    if not last_datetime:
        CHAT_BY_DATETIME[callback.message.chat.id] = current_time
        getNews('Kartinamaslom5')
        with open('tweets.json',encoding="utf8") as file:
            data = json.load(file)
            if len(data) !=0:
                for message_ in data:
                    newNews = f"{hbold('Дата :')} {message_.get('date')}\n"\
                        f"{hbold('Новость:')} {message_.get('tweet')}\n"\
                        f"{hbold('Подробности:')} {message_.get('url')}\n"
                    await callback.message.answer(newNews)
            else:
                await callback.message.answer('Новостей нет! Совсем нет!') 
    else:
        # Разница в секундах между текущим временем и временем последнего сообщения
        delta_seconds = (current_time - last_datetime).total_seconds()
        # Осталось ждать секунд перед отправкой
        seconds_left = int(need_seconds - delta_seconds)
        # Если время ожидания не закончилось
        if seconds_left > 0:
             text = f'Подождите {seconds_left} секунд перед выполнение этой команды'
        else:
            CHAT_BY_DATETIME[callback.message.chat.id] = current_time
            getNews('Kartinamaslom5')
            with open('tweets.json',encoding="utf8") as file:
                data = json.load(file)
                if len(data) !=0:
                    for message_ in data:
                        newNews = f"{hbold('Дата :')} {message_.get('date')}\n"\
                            f"{hbold('Новость:')} {message_.get('tweet')}\n"\
                            f"{hbold('Подробности:')} {message_.get('url')}\n"
                        await callback.message.answer(newNews)
                else:
                    await callback.message.answer('Новостей нет! Совсем нет!') 
            
        await callback.message.answer(text)
                
   
# запускаем программу
if __name__ == '__main__':
# указание skip_updates=True
# пропустит команды,
# которые отправили
# до старта бота
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



