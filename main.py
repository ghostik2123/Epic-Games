import requests
import telebot
from io import BytesIO
from PIL import Image
import schedule
import threading
import time


bot = telebot.TeleBot("YOU_TOKEN_TELEGRAM")

def delete_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)

def schedule_delete_message(chat_id, message_id, delay):
    schedule.every(delay).seconds.do(delete_message, chat_id, message_id)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def start(message):
    """Отправляет сообщение пользователю при получении команды /start."""
    bot.reply_to(message, "Добро пожаловать в бот Epic Games Store! Используйте команду /games, чтобы увидеть список бесплатных игр.")

@bot.message_handler(commands=['games'])
def games(message):
    response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru-RU&country=RU&allowCountries=RU")
    data = response.json()
    games_list = data["data"]["Catalog"]["searchStore"]["elements"]
    
    for game in games_list:
        title = game["title"]
        description = game.get("description", "Описание отсутствует")
        image_url = next((img["url"] for img in game["keyImages"] if img["type"] == "OfferImageWide"), None)
        
        if image_url:
            image_response = requests.get(image_url)
            image_data = BytesIO(image_response.content)
            image = Image.open(image_data)
            
            sent_message = bot.send_photo(message.chat.id, image, caption=f"{title}\nОписание: {description}")
            
            schedule_delete_message(message.chat.id, sent_message.message_id, 60)
        else:
            bot.reply_to(message, f"{title}\nОписание: {description}\nИзображение отсутствует")

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

bot.infinity_polling()
