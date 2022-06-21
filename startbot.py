from aiogram import Bot, Dispatcher,types
from aiogram.utils import executor
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import tweepy
import json
import re
from config import settings
from FromTwitter import TwitterMedia

# Работа с твиттером
Tweet = []

def getNews(twitterName):
    Tweet = []
    consumer_key = settings['consumer_key']
    consumer_secret = settings['consumer_secret']
    access_token = settings['access_token']
    access_token_secret = settings['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    search_words  = "#UkraineRussiaWar"      # фильтр по хештегам
    search_words2 = "#Ukrainewar"
    api = tweepy.API(auth, proxy='')
    tweets_list= api.user_timeline(screen_name=twitterName, count=3,tweet_mode="extended",include_rts=False) # Get the last tweet

    tweet= tweets_list
    for element in tweet:
        if search_words in str(element.full_text) or search_words2 in str(element.full_text):
            media = element.entities.get('media', [])
            if(len(media) > 0):
                url_media = media[0]['media_url']
                # Созаем список словарей
                Tweet.append({
                    "date"  : element.created_at,
                    "tweet" : re.sub(r'(," ")(?=$)',r'',re.sub(r"https?://[^,\s]+,?", "", element.full_text)),
                    "url"   : url_media})
    # сохраяем в файл       
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

InlKB = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Получить последние новости',callback_data='News'))

# Хендлеры бота

@dp.message_handler(commands=['start','help'])
async def command_start(message : types.Message):
    await bot.send_message(message.chat.id,'Бот запущен. Жди хороших новостей или не очень',reply_markup=InlKB)

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
    News = getNews('Kartinamaslom5')
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

# запускаем программу
if __name__ == '__main__':
# указание skip_updates=True
# пропустит команды,
# которые отправили
# до старта бота
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



