import telebot
import os
from dotenv import load_dotenv
import DB_utils as db
load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

@bot.message_handler(commands=["start"])
def start(message, res=False):

    telebot.types.ReplyKeyboardRemove()

    bot.send_message(message.chat.id, 'Здравствуйте - это бот для легкой работы')

    db.CreateTable()
    db.NewUser(message.chat.id)

bot.polling(none_stop=True, interval=0, timeout=0)

