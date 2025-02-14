import telebot
from telebot import types
import os
from dotenv import load_dotenv
import DB_utils as db
import SOURCE
import random
import TONmanager as ton

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))
invoices = {}


@bot.message_handler(commands=["start"])
def start(message, res=False):
    # db.CreateTable()  # TODO: вырезать после завершения тестов
    btns = []
    for i in SOURCE.channels_url:
        result = bot.get_chat_member(str('@'+i[i.rfind('/')+1:]), message.chat.id)
        # print(result, message.chat.id)
        if result.status != 'member' and result.status != 'creator':
            markup = types.InlineKeyboardMarkup()
            for j in SOURCE.channels_url:
                channelBtn = types.InlineKeyboardButton(
                    str(SOURCE.getText('channelNum', SOURCE.default_language).format(
                        num=SOURCE.channels_url.index(j) + 1)),
                    url=j)
                btns.append(channelBtn)

            for btn in btns:
                markup.add(btn)
            checkBtn = types.InlineKeyboardButton(SOURCE.getText('checkBtn', SOURCE.default_language),callback_data=SOURCE.channel_check)

            markup.add(checkBtn)
            bot.send_message(message.chat.id, SOURCE.getText('noMember', SOURCE.default_language), reply_markup=markup)
            return

    if db.isNew(message.chat.id):
        if str(message.chat.id) in os.getenv('ADMINS'):
            db.newAdmin(message)
            return

        if " " in message.text:
            referrer_candidate = message.text.split()[1]

            # Пробуем преобразовать строку в число
            try:
                referrer_candidate = int(referrer_candidate)

                # Проверяем на несоответствие TG ID пользователя TG ID реферера
                if message.chat.id != referrer_candidate:
                    db.setReferral(referrer_candidate)

            except ValueError:
                pass

        telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, SOURCE.getText('start_text', SOURCE.default_language))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        executorBtn = types.KeyboardButton(SOURCE.getText('employer', SOURCE.default_language))
        employerBtn = types.KeyboardButton(SOURCE.getText('executor', SOURCE.default_language))
        markup.add(employerBtn, executorBtn)

        bot.send_message(message.chat.id, SOURCE.getText('choose_role', SOURCE.default_language),
                         reply_markup=markup)
        bot.register_next_step_handler(message, db.NewUser)
        return

    # bot.send_message(message.chat.id, SOURCE.getText('start_text_second', db.getLanguage(message.chat.id)))
    if str(message.chat.id) in os.getenv('ADMINS'):
        adminPanelView(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    executorBtn = types.KeyboardButton(SOURCE.getText('employer',  db.getLanguage(message.chat.id)))
    employerBtn = types.KeyboardButton(SOURCE.getText('executor',  db.getLanguage(message.chat.id)))
    markup.add(employerBtn, executorBtn)

    bot.send_message(message.chat.id, SOURCE.getText('changeRole', db.getLanguage(message.chat.id)), reply_markup=markup)
    bot.register_next_step_handler(message, db.setRole)

    return


def adminPanelView(message):
    language = db.getLanguage(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    statisticBtn = types.KeyboardButton(SOURCE.getText('statisticBtn', language))
    tasksBtn = types.KeyboardButton(SOURCE.getText('tasksBtn', language))
    mailingBtn = types.KeyboardButton(SOURCE.getText('mailingBtn', language))
    withdrawRequests = types.KeyboardButton(SOURCE.getText('withdrawRequests', language))

    markup.add(statisticBtn)
    markup.add(mailingBtn)
    markup.add(tasksBtn)
    markup.add(withdrawRequests)

    bot.send_message(message.chat.id, SOURCE.getText('welcomeAdminText', db.getLanguage(message.chat.id)),
                     reply_markup=markup)


@bot.message_handler(func=lambda message: str(message.chat.id) in os.getenv('ADMINS'))
def adminPanel(message):
    language = db.getLanguage(message.chat.id)

    if message.text == SOURCE.getText('statisticBtn', language):
        statistic = db.getStatistic()
        bot.send_message(message.chat.id,
                         str(SOURCE.getText('statisticText', language)).format(employer_count=statistic[0],
                                                                               executor_count=statistic[1],
                                                                               tasks_activity_count=statistic[2]))
    if message.text == SOURCE.getText('mailingBtn', language):
        chancelBtn = types.KeyboardButton(SOURCE.getText('chancelMailingBtn', language))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(chancelBtn)
        bot.send_message(message.chat.id, SOURCE.getText('mailingWait', language), reply_markup=markup)
        bot.register_next_step_handler(message, mailing)

    if message.text == SOURCE.getText('tasksBtn', language):
        tasks = db.getTasks(message.chat.id, db.getRole(message.chat.id))

        if not tasks:
            bot.send_message(message.chat.id, SOURCE.getText('noTask', language))
            return

        for i in tasks:
            bot.send_message(message.chat.id,
                             str(SOURCE.getText('taskTextTemplate', language)
                                 .format(text=i[0],
                                         price=db.getPrice(i[1]))))

    if message.text == SOURCE.getText('withdrawRequests', language):
        req = db.getMoneyRequests()
        for i in req:
            payBtn = types.InlineKeyboardButton(SOURCE.getText('payBtn', language), url=str(i[3]))
            completeBtn = types.InlineKeyboardButton(SOURCE.getText('completeWithdrawBtn', language),
                                                     callback_data=SOURCE.withdraw_complete + '|' + str(i[0]))
            markup = types.InlineKeyboardMarkup().add(payBtn, completeBtn)
            bot.send_message(message.chat.id,
                             str(SOURCE.getText('moneyRequestTemplate', language).format(username=i[1], money=i[2])),
                             reply_markup=markup)


def mailing(message):
    if message.text == SOURCE.getText('chancelMailingBtn', db.getLanguage(message.chat.id)):
        adminPanelView(message)
        return
    for i in db.getUsers():
        if i[0] == message.chat.id:
            continue
        bot.send_message(i[0], message.text)
    bot.send_message(message.chat.id, SOURCE.getText('mailingComplete', db.getLanguage(message.chat.id)))
    adminPanelView(message)


@bot.message_handler()
def TextHandler(message):
    btns = []
    for i in SOURCE.channels_url:

        result = bot.get_chat_member(str('@' + i[i.rfind('/') + 1:]), message.chat.id)
        # print(result, message.chat.id)
        if result.status != 'member' and result.status != 'creator':
            markup = types.InlineKeyboardMarkup()
            for j in SOURCE.channels_url:
                channelBtn = types.InlineKeyboardButton(
                    str(SOURCE.getText('channelNum', SOURCE.default_language).format(
                        num=SOURCE.channels_url.index(j) + 1)),
                    url=j)
                btns.append(channelBtn)

            for btn in btns:
                markup.add(btn)
            checkBtn = types.InlineKeyboardButton(SOURCE.getText('checkBtn', SOURCE.default_language),
                                                  callback_data=SOURCE.channel_check)

            markup.add(checkBtn)
            bot.send_message(message.chat.id, SOURCE.getText('noMember', SOURCE.default_language),
                             reply_markup=markup)
            return

    if db.isNew(message.chat.id):
        bot.send_message(message.chat.id, SOURCE.getText('notRegistered', SOURCE.default_language))
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
        howCreateTaskBtn = types.KeyboardButton(SOURCE.getText('howCreateTaskBtn', language))
        profileBtn = types.KeyboardButton(SOURCE.getText("profileBtn", language))

        # Добавляем кнопки в клавиатуру
        markup.add(viewTasksBtn, profileBtn)  # Можно добавлять по несколько кнопок в ряд
        markup.add(newTaskBtn, howCreateTaskBtn)

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
            createReferralBtn = types.KeyboardButton(SOURCE.getText('createReferralBtn', language))
            goToMenu = types.KeyboardButton(SOURCE.getText('goToMenu', language))

            markup.add(topUpBalanceBtn)
            markup.add(changeLanguageBtn)
            markup.add(createReferralBtn)
            markup.add(goToMenu)

            bot.send_message(message.chat.id,
                             str(SOURCE.getText('profileEmployerText', language)
                                 .format(balance=db.getBalance(message.chat.id),
                                         createTask=db.getCreateTasks(message.chat.id)
                                         )),
                             reply_markup=markup)
        if message.text == SOURCE.getText('howCreateTaskBtn', language):
            bot.send_message(message.chat.id,SOURCE.getText('howCreateTaskText', language))
        if message.text == SOURCE.getText("viewTasksBtn", language):
            tasks = db.getTasks(message.chat.id, db.getRole(message.chat.id))

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
            withdrawBalanceBtn = types.KeyboardButton(SOURCE.getText('withdrawBalanceBtn', language))
            createReferralBtn = types.KeyboardButton(SOURCE.getText('createReferralBtn', language))
            goToMenu = types.KeyboardButton(SOURCE.getText('goToMenu', language))

            markup.add(withdrawBalanceBtn)
            markup.add(changeLanguageBtn)
            markup.add(createReferralBtn)
            markup.add(goToMenu)

            bot.send_message(message.chat.id,
                             str(SOURCE.getText('profileExecutorText', language)
                                 .format(balance=db.getBalance(message.chat.id),
                                         completeTask=db.getCompleteTasks(message.chat.id))),
                             reply_markup=markup)

        if message.text == SOURCE.getText("viewTasksBtn", language):
            tasks = db.getTasks(role=db.getRole(message.chat.id))

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


def withdrawMoney(message):
    if message.text == SOURCE.chancel_withdraw_balance:
        mainMenuView(message)
        return
    if message.text == SOURCE.getText('allMoneyBtn', db.getLanguage(message.chat.id)):
        value = db.getBalance(message.chat.id)
    else:
        value = message.text
    if db.isHaveRequest(message.chat.id):
        db.setHowMuchMoney(message.chat.id, value)
        mainMenuView(message)
        return

    bot.send_message(message.chat.id, SOURCE.getText('getLinks', db.getLanguage(message.chat.id)))
    bot.register_next_step_handler(message, db.newMoneyRequests, value)


def profileOnClick(message):
    role = db.getRole(message.chat.id)
    language = db.getLanguage(message.chat.id)

    if message.text == SOURCE.getText('withdrawBalanceBtn', language) and role == SOURCE.executor:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        allMoneyBtn = types.KeyboardButton(SOURCE.getText('allMoneyBtn', language))
        chancelWithdrawBtn = types.KeyboardButton(SOURCE.getText('chancelWithdrawBtn', language))

        markup.add(allMoneyBtn)
        markup.add(chancelWithdrawBtn)

        bot.send_message(message.chat.id,
                         str(SOURCE.getText('withdrawBalanceAmountText', language).format(
                             balance=db.getBalance(message.chat.id))),
                         reply_markup=markup)
        bot.register_next_step_handler(message, withdrawMoney)

    if message.text == SOURCE.getText('topUpBalanceBtn', language) and role == SOURCE.employer:
        bot.send_message(message.chat.id, SOURCE.getText('getAmountText', language))
        bot.register_next_step_handler(message, setAmountPayment)

    if message.text == SOURCE.getText('createReferralBtn', language):
        bot.send_message(message.chat.id, SOURCE.getText('youGetReferral', language))
        bot.send_message(message.chat.id, str(SOURCE.referral_url.format(user_id=message.chat.id)))

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


def setAmountPayment(message):
    try:
        price = float(message.text.replace(',', '.'))
    except:
        bot.send_message(message.chat.id, SOURCE.getText('noIntPrice', db.getLanguage(message.chat.id)))
        return
    if price < SOURCE.min_money:
        bot.send_message(message.chat.id,
                         str(SOURCE.getText('minMoneyText',
                                            db.getLanguage(message.chat.id)).format(min_money=SOURCE.min_money)))
        return
    bot.send_message(message.chat.id, ton.get_invoice(message, price))


def getPrice(message):
    text = message.text

    bot.send_message(message.chat.id, SOURCE.getText('getPriceText', db.getLanguage(message.chat.id)))
    bot.register_next_step_handler(message, db.newTask, text)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if SOURCE.channel_check in callback.data:
        btns = []
        for i in SOURCE.channels_url:

            result = bot.get_chat_member(str('@' + i[i.rfind('/') + 1:]), callback.message.chat.id)
            # print(result, message.chat.id)
            if result.status != 'member' and result.status != 'creator':
                markup = types.InlineKeyboardMarkup()
                for j in SOURCE.channels_url:

                    channelBtn = types.InlineKeyboardButton(
                        str(SOURCE.getText('channelNum', SOURCE.default_language).format(
                            num=SOURCE.channels_url.index(j) + 1)),
                        url=j)
                    btns.append(channelBtn)

                for btn in btns:
                    markup.add(btn)
                checkBtn = types.InlineKeyboardButton(SOURCE.getText('checkBtn', SOURCE.default_language),
                                                      callback_data=SOURCE.channel_check)

                markup.add(checkBtn)
                bot.send_message(callback.message.chat.id, SOURCE.getText('noMember', SOURCE.default_language),
                                 reply_markup=markup)
                return
        bot.send_message(callback.message.chat.id, SOURCE.getText('youSubChannel', SOURCE.default_language))
        if db.isNew(callback.message.chat.id):
            bot.send_message(callback.message.chat.id, SOURCE.getText('youCanContinueRegister', SOURCE.default_language))
        return

    language = db.getLanguage(callback.message.chat.id)

    if SOURCE.withdraw_complete in callback.data:
        userId = callback.data[callback.data.find('|') + 1:]
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        db.setBalance(userId, str(-1 * db.getMoneyFromRequest(userId)))
        db.deleteMoneyRequest(userId)
        bot.send_message(userId, SOURCE.getText('moneyWithdrawComplete', db.getLanguage(userId)))
        bot.send_message(callback.message.chat.id, SOURCE.getText('moneyWithdrawCompleteAdminText', language))
    if SOURCE.ruChange in callback.data:
        db.setLanguage(callback.message.chat.id, SOURCE.ruChange)
        bot.send_message(callback.message.chat.id, SOURCE.getText('changeLanguageComplete', language))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        mainMenuView(callback.message)

    if SOURCE.enChange in callback.data:
        db.setLanguage(callback.message.chat.id, SOURCE.enChange)
        bot.send_message(callback.message.chat.id, SOURCE.getText('changeLanguageComplete', language))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        mainMenuView(callback.message)

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
