import telebot
from telebot import types
import os
from dotenv import load_dotenv
import DB_utils as db
import SOURCE
import random

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
        mainMenuView(message)


@bot.message_handler()
def TextHandler(message):
    if db.isNew(message.chat.id):
        bot.send_message(message.chat.id, SOURCE.getText('notRegistered', message.from_user.language_code))
        return
    mainMenuOnCLick(message)
    profileOnClick(message)


def anotherMessage(id, text):
    bot.send_message(id, text)


def mainMenuView(message):
    """
       Создает и отправляет главное меню пользователю в зависимости от его роли.
       """

    user_id = message.chat.id
    role = db.getRole(user_id)
    language = db.getLanguage(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if role == SOURCE.employer:
        # Создаем кнопки для работодателя
        viewTasksBtn = types.KeyboardButton(SOURCE.getText("viewTasksBtn", language))
        newTaskBtn = types.KeyboardButton(SOURCE.getText("newTaskBtn", language))
        profileBtn = types.KeyboardButton(SOURCE.getText("profileBtn", language))

        # Добавляем кнопки в клавиатуру
        markup.add(viewTasksBtn, profileBtn)  # Можно добавлять по несколько кнопок в ряд
        markup.add(newTaskBtn)

    elif role == SOURCE.executor:
        # Создаем кнопки для исполнителя
        viewTasksBtn = types.KeyboardButton(SOURCE.getText("viewTasksBtn", language))
        profileBtn = types.KeyboardButton(SOURCE.getText("profileBtn", language))

        # Добавляем кнопки в клавиатуру
        markup.add(viewTasksBtn, profileBtn)

    # Отправляем сообщение с главным меню
    bot.send_message(user_id, SOURCE.getText('mainMenu', language), reply_markup=markup)


def mainMenuOnCLick(message):
    role = db.getRole(message.chat.id)
    language = db.getLanguage(message.chat.id)

    if role == SOURCE.employer:
        if message.text == SOURCE.getText("profileBtn", language):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            changeLanguageBtn = types.KeyboardButton(SOURCE.getText('changeLanguageBtn', language))
            topUpBalanceBtn = types.KeyboardButton(SOURCE.getText('topUpBalanceBtn', language))
            goToMenu = types.KeyboardButton(SOURCE.getText('goToMenu', language))
            markup.add(topUpBalanceBtn)
            markup.add(changeLanguageBtn)
            markup.add(goToMenu)

            bot.send_message(message.chat.id,
                             str(SOURCE.getText('profileEmployerText', language)
                                 .format(balance=db.getBalance(message.chat.id),
                                         createTask=db.getCreateTasks(message.chat.id),
                                         code=' 3')),
                             reply_markup=markup)

        if message.text == SOURCE.getText("viewTasksBtn", language):
            tasks = db.getTasks(message.chat.id)

            if not tasks:
                bot.send_message(message.chat.id, SOURCE.getText('noTask', language))
                return

            for i in tasks:
                markup = types.InlineKeyboardMarkup()
                dealeteBtn = types.InlineKeyboardButton(SOURCE.getText('deleteBtn', language),
                                                        callback_data=SOURCE.deleteCallback + '|' + str(i[1]))
                markup.add(dealeteBtn)

                bot.send_message(message.chat.id,
                                 str(SOURCE.getText('taskTextTemplate', language)
                                     .format(text=i[0],
                                             price=db.getPrice(i[1]))),
                                 reply_markup=markup)

        if message.text == SOURCE.getText("newTaskBtn", db.getLanguage(message.chat.id)):
            db.setCreateTasks(message.chat.id)
            bot.send_message(message.chat.id, SOURCE.getText('newTaskText', language))
            bot.register_next_step_handler(message, getPrice)

    if role == SOURCE.executor:
        if message.text == SOURCE.getText("profileBtn", language):

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            changeLanguageBtn = types.KeyboardButton(SOURCE.getText('changeLanguageBtn', language))
            withdrawBalanceBtn= types.KeyboardButton(SOURCE.getText('withdrawBalanceBtn', language))
            goToMenu = types.KeyboardButton(SOURCE.getText('goToMenu', language))
            markup.add(withdrawBalanceBtn)
            markup.add(changeLanguageBtn)
            markup.add(goToMenu)

            bot.send_message(message.chat.id,
                             str(SOURCE.getText('profileExecutorText', language)
                                 .format(balance=db.getBalance(message.chat.id),
                                         completeTask=db.getCompleteTasks(message.chat.id),
                                         code=' 3')),
                             reply_markup=markup)

        if message.text == SOURCE.getText("viewTasksBtn", language):
            tasks = db.getTasks()

            if not tasks:
                bot.send_message(message.chat.id, SOURCE.getText('notTaskToday', language))
                return
            tasksNum = random.randint(0, len(tasks) - 1)
            markup = types.InlineKeyboardMarkup()
            respondBtn = types.InlineKeyboardButton(SOURCE.getText('respondBtn', language),
                                                    callback_data=SOURCE.respondCallback + '|'
                                                                  + str(tasks[tasksNum][1]))
            markup.add(respondBtn)
            bot.send_message(message.chat.id, str(SOURCE.getText('taskTextTemplate', language)
                                                  .format(text=tasks[random.randint(0, len(tasks) - 1)][0],
                                                          price=db.getPrice(tasks[tasksNum][1]))),
                             reply_markup=markup)

def profileOnClick(message):
    role = db.getRole(message.chat.id)
    language = db.getLanguage(message.chat.id)

    if message.text == SOURCE.getText('changeLanguageBtn', language):
        markup = types.InlineKeyboardMarkup()
        ruBtn = types.InlineKeyboardButton(SOURCE.getText('ruBtn', language),
                                           callback_data=SOURCE.ruChange)
        enBtn = types.InlineKeyboardButton(SOURCE.getText('enBtn', language),
                                           callback_data=SOURCE.enChange)
        markup.add(ruBtn, enBtn)
        bot.send_message(message.chat.id, SOURCE.getText('changeLanguage', language), reply_markup=markup)

    if message.text == SOURCE.getText('goToMenu', language):
        mainMenuView(message)


def getPrice(message):
    text = message.text
    bot.send_message(message.chat.id, SOURCE.getText('getPriceText', db.getLanguage(message.chat.id)))
    bot.register_next_step_handler(message, db.newTask, text)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    language = db.getLanguage(callback.message.chat.id)

    if SOURCE.ruChange in callback.data:
        db.setLanguage(callback.message.chat.id, SOURCE.ruChange)
        bot.send_message(callback.message.chat.id,SOURCE.getText('changeLanguageComplete', language))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.enChange in callback.data:
        db.setLanguage(callback.message.chat.id, SOURCE.enChange)
        bot.send_message(callback.message.chat.id, SOURCE.getText('changeLanguageComplete', language))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.deleteCallback in callback.data:
        taskId = callback.data[callback.data.find('|') + 1:]
        db.deleteTask(taskId)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.respondCallback in callback.data:
        taskId = callback.data[callback.data.find('|') + 1:]
        bot.send_message(callback.message.chat.id,
                         SOURCE.getText('sendReport', language))
        bot.register_next_step_handler(callback.message, get_photo, db.getEmployerId(taskId), taskId)

    if SOURCE.closeReport in callback.data:
        executorID = callback.data[callback.data.find('|') + 1:]
        taskId = callback.data[callback.data.rfind('|') + 1:]
        db.setRating(executorID, -1)
        db.setTaskActivity(taskId, SOURCE.db_True)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if SOURCE.acceptReport in callback.data:
        executorID = callback.data[callback.data.find('|') + 1:callback.data.rfind('|')]
        taskId = callback.data[callback.data.rfind('|') + 1:]
        db.setRating(executorID, 1)
        db.setCompleteTasks(executorID)
        db.deleteTask(taskId)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.message_handler(content_types=['photo'])
def get_photo(message, employerID=None, taskId=None):
    if employerID is None or taskId is None:
        return

    bot.copy_message(chat_id=employerID, from_chat_id=message.chat.id, message_id=message.message_id)
    db.setTaskActivity(taskId, SOURCE.db_False)
    db.setTaskExecutorId(taskId, message.chat.id)
    markup = types.InlineKeyboardMarkup()

    acceptBtn = types.InlineKeyboardButton(SOURCE.getText('acceptBtn', db.getLanguage(employerID)),
                                           callback_data=SOURCE.acceptReport + '|' + str(
                                               message.chat.id) + '|' + taskId)
    closeBtn = types.InlineKeyboardButton(SOURCE.getText('closeBtn', db.getLanguage(employerID)),
                                          callback_data=SOURCE.closeReport + '|' + str(message.chat.id) + '|' + taskId)
    markup.add(acceptBtn, closeBtn)

    bot.send_message(employerID,
                     SOURCE.getText('reportForEmployer', db.getLanguage(employerID)) + ' ' + db.getTask(taskId),
                     reply_markup=markup)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0, timeout=0)
