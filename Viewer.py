import telebot
from telebot import types
import os
from dotenv import load_dotenv
import DB_utils as db

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=["start"])
def start(message, res=False):
    telebot.types.ReplyKeyboardRemove()
    db.CreateTable()
    if db.isNew(message.chat.id):
        bot.send_message(message.chat.id, 'Здравствуйте - это бот для легкой работы')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        executorBtn = types.KeyboardButton("Исполнитель")
        employerBtn = types.KeyboardButton("Заказчик")
        markup.add(employerBtn, executorBtn)

        bot.send_message(message.chat.id, 'Выберите вашу роль', reply_markup=markup)
        bot.register_next_step_handler(message, db.NewUser)
        

    else:
        bot.send_message(message.chat.id, 'Здравствуйте еще раз')


@bot.message_handler()
def TextHandler(message):
    print(message.text)


bot.polling(none_stop=True, interval=0, timeout=0)
