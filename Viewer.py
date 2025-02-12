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
    db.CreateTable()  # вырезать, когда будет готова админ панель
    #
    # print(bot.get_chat_member(Channel_id message.chat.id))
    # print("pod")

    if db.isNew(message.chat.id):

        telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, SOURCE.getText('start_text', message.from_user.language_code))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        executorBtn = types.KeyboardButton(SOURCE.getText('employer', message.from_user.language_code))
        employerBtn = types.KeyboardButton(SOURCE.getText('executor', message.from_user.language_code))
        markup.add(employerBtn, executorBtn)

        bot.send_message(message.chat.id, SOURCE.getText('choose_role', message.from_user.language_code),
                         reply_markup=markup)
        bot.register_next_step_handler(message, db.NewUser)

    else:
        bot.send_message(message.chat.id, SOURCE.getText('start_text_second', db.getLanguage(message.chat.id)))

@bot.message_handler()
def TextHandler(message):
    if db.isNew(message.chat.id):

        bot.send_message(message.chat.id, SOURCE.getText('notRegistered', message.from_user.language_code))
        return
    mainMenuOnCLick(message)


def anotherMessage(id, text):
    bot.send_message(id, text)


def mainMenuView(message):
    role = db.getRole(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == SOURCE.employer:
        viewTasksBtn = types.KeyboardButton(SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)))
        newTaskBtn = types.KeyboardButton(SOURCE.getText("newTaskBtn", db.getLanguage(message.chat.id)))
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
        if message.text == SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)):

            for i in db.getTasks(message.chat.id):
                markup = types.InlineKeyboardMarkup()
                dealeteBtn = types.InlineKeyboardButton(SOURCE.getText('deleteBtn', db.getLanguage(message.chat.id)),
                                                        callback_data=SOURCE.deleteCallback + '|' + str(i[1]))
                markup.add(dealeteBtn)
                bot.send_message(message.chat.id, i[0], reply_markup=markup)

        if message.text == SOURCE.getText("newTaskBtn", db.getLanguage(message.chat.id)):
            bot.send_message(message.chat.id, SOURCE.getText('newTaskText', db.getLanguage(message.chat.id)))
            bot.register_next_step_handler(message, db.newTask)

    if role == SOURCE.executor:

        if message.text == SOURCE.getText("viewTasksBtn", db.getLanguage(message.chat.id)):
            for i in db.getTasks():
                markup = types.InlineKeyboardMarkup()
                respondBtn = types.InlineKeyboardButton(SOURCE.getText('respondBtn', db.getLanguage(message.chat.id)),
                                                        callback_data=SOURCE.respondCallback + '|' + str(i[1]))
                markup.add(respondBtn)
                bot.send_message(message.chat.id, i, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if SOURCE.deleteCallback in callback.data:
        taskId = callback.data[callback.data.find('|') + 1:]
        db.deleteTask(taskId)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.respondCallback in callback.data:
        taskId = callback.data[callback.data.find('|') + 1:]
        bot.send_message(callback.message.chat.id,
                         SOURCE.getText('sendReport', db.getLanguage(callback.message.chat.id)))
        bot.register_next_step_handler(callback.message, get_photo, db.getEmployerId(taskId), taskId)

    if SOURCE.closeReport in callback.data:
        executorID = callback.data[callback.data.find('|') + 1:]
        db.setRating(executorID, -1)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.acceptReport in callback.data:
        executorID = callback.data[callback.data.find('|') + 1:]
        db.setRating(executorID, 1)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.message_handler(content_types=['photo'])
def get_photo(message, employerID=None, taskId=None):
    if employerID is None or taskId is None:
        return

    bot.copy_message(chat_id=employerID, from_chat_id=message.chat.id, message_id=message.message_id)
    db.setTaskActivity(taskId, 'FALSE')
    db.setTaskExecutorId(taskId,message.chat.id)
    markup = types.InlineKeyboardMarkup()
    acceptBtn = types.InlineKeyboardButton(SOURCE.getText('acceptBtn', db.getLanguage(employerID)),
                                           callback_data=SOURCE.acceptReport+'|'+str(message.chat.id))
    closeBtn = types.InlineKeyboardButton(SOURCE.getText('closeBtn', db.getLanguage(employerID)),
                                          callback_data=SOURCE.closeReport+'|'+str(message.chat.id))
    markup.add(acceptBtn, closeBtn)

    bot.send_message(employerID,
                     SOURCE.getText('reportForEmployer', db.getLanguage(employerID)) + ' ' + db.getTask(taskId),
                     reply_markup=markup)





if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0, timeout=0)
