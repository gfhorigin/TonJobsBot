import telebot
from telebot import types
import os
from dotenv import load_dotenv
import DB_utils as db
import SOURCE

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=["start"])
def start(message, res=False):


    db.CreateTable() #вырезать, когда будет готова админ панель

    if db.isNew(message.chat.id):
        telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,SOURCE.getText('start_text', message.from_user.language_code))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        executorBtn = types.KeyboardButton(SOURCE.getText('employer', message.from_user.language_code))
        employerBtn = types.KeyboardButton(SOURCE.getText('executor', message.from_user.language_code))
        markup.add(employerBtn, executorBtn)

        bot.send_message(message.chat.id, SOURCE.getText('choose_role', message.from_user.language_code),
                         reply_markup=markup)
        bot.register_next_step_handler(message, db.NewUser)

    else:
        bot.send_message(message.chat.id, SOURCE.getText('start_text_second', db.getLanguage(message.chat.id)))

def anotherMessage(id,text):
    bot.send_message(id,text)

def mainMenuView(message):
    role = db.getRole(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == SOURCE.employer:

        viewTasksBtn = types.KeyboardButton(SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)))
        newTaskBtn  = types.KeyboardButton(SOURCE.getText("newTaskBtn", db.getLanguage(message.chat.id)))
        profileBtn = types.KeyboardButton(SOURCE.getText("profileBtn", db.getLanguage(message.chat.id)))
        markup.add(viewTasksBtn)
        markup.add(profileBtn)
        markup.add(newTaskBtn)
    if role == SOURCE.executor:
        viewTasksBtn = types.KeyboardButton(SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)))
        profileBtn = types.KeyboardButton(SOURCE.getText("profileBtn", db.getLanguage(message.chat.id)))
        markup.add(viewTasksBtn)
        markup.add(profileBtn)

    bot.send_message(message.chat.id, SOURCE.getText('mainMenu', db.getLanguage(message.chat.id)),
                                                        reply_markup=markup)

def mainMenuOnCLick(message):
    role = db.getRole(message.chat.id)

    if role == SOURCE.employer:
        if message.text ==  SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)):
            for i in db.getTasks(message.chat.id):
                bot.send_message(message.chat.id, i)
    if role == SOURCE.executor:
        if message.text ==  SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)):
            for i in db.getTasks():
                bot.send_message(message.chat.id, i)

@bot.message_handler()
def TextHandler(message):
    mainMenuOnCLick(message)

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0, timeout=0)
