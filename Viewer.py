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
    db.CreateTable()  # TODO: вырезать после завершения тестов
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
            bot.send_message(message.chat.id, SOURCE.getText('noMember', SOURCE.default_language), reply_markup=markup)
            return

    if db.isNew(message.chat.id):
        if str(message.chat.id) in os.getenv('ADMINS'):
            db.newAdmin(message)
            return
        base_money = 0
        if " " in message.text:
            referrer_candidate = message.text.split()[1]
            # print(referrer_candidate)
            # Пробуем преобразовать строку в число
            try:
                referrer_candidate = int(referrer_candidate)

                # Проверяем на несоответствие TG ID пользователя TG ID реферера
                if message.chat.id != referrer_candidate:
                    bot.send_message(referrer_candidate, SOURCE.getText('referralRegister', SOURCE.default_language))
                    db.setReferral(referrer_candidate)
                    base_money = SOURCE.for_referral_money
                    db.setBalance(referrer_candidate, SOURCE.for_referral_money)

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

        bot.register_next_step_handler(message, db.NewUser, base_money)
        return

    # bot.send_message(message.chat.id, SOURCE.getText('start_text_second', db.getLanguage(message.chat.id)))
    if str(message.chat.id) in os.getenv('ADMINS'):
        adminPanelView(message)
        return
    if db.isBan(message.chat.id):
        bot.send_message(message.chat.id, SOURCE.getText('youBanned', db.getLanguage(message.chat.id)))
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    executorBtn = types.KeyboardButton(SOURCE.getText('employer', db.getLanguage(message.chat.id)))
    employerBtn = types.KeyboardButton(SOURCE.getText('executor', db.getLanguage(message.chat.id)))
    markup.add(employerBtn, executorBtn)

    bot.send_message(message.chat.id, SOURCE.getText('changeRole', db.getLanguage(message.chat.id)),
                     reply_markup=markup)
    bot.register_next_step_handler(message, db.setRole)

    return


def adminPanelView(message):
    language = db.getLanguage(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    statisticBtn = types.KeyboardButton(SOURCE.getText('statisticBtn', language))
    tasksBtn = types.KeyboardButton(SOURCE.getText('tasksBtn', language))
    mailingBtn = types.KeyboardButton(SOURCE.getText('mailingBtn', language))
    withdrawRequests = types.KeyboardButton(SOURCE.getText('withdrawRequests', language))
    userListBtn = types.KeyboardButton(SOURCE.getText('userListBtn', language))

    markup.add(statisticBtn)
    markup.add(mailingBtn)
    markup.add(tasksBtn)
    markup.add(withdrawRequests)
    markup.add(userListBtn)

    bot.send_message(message.chat.id, SOURCE.getText('welcomeAdminText', db.getLanguage(message.chat.id)),
                     reply_markup=markup)


@bot.message_handler(func=lambda message: str(message.chat.id) in os.getenv('ADMINS'))
def adminPanel(message):
    language = db.getLanguage(message.chat.id)

    if message.text == SOURCE.getText('userListBtn', language):
        usersInfo = db.getUsersInfo()
        for userInfo in usersInfo:
            if userInfo[3] == message.chat.id:
                continue
            markup = types.InlineKeyboardMarkup()
            if db.isBan(userInfo[3]):
                banBtn = types.InlineKeyboardButton(SOURCE.getText('unbanBtn', language),
                                                    callback_data=str(SOURCE.unban) + '|' + str(userInfo[3]))
            else:
                banBtn = types.InlineKeyboardButton(SOURCE.getText('banBtn', language),
                                                    callback_data=str(SOURCE.ban) + '|' + str(userInfo[3]))

            setBalanceBtn = types.InlineKeyboardButton(SOURCE.getText('setBalanceBtn', language),
                                                       callback_data=SOURCE.set_balance_command + '|' + str(
                                                           userInfo[3]))
            markup.add(banBtn, setBalanceBtn)
            bot.send_message(message.chat.id,
                             SOURCE.getText('userInfoForAdmin', language).format(username=userInfo[0] if userInfo[0] else str(userInfo[3]),
                                                                                 balance=userInfo[1],
                                                                                 referral=userInfo[2]),
                             reply_markup=markup)

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
        if not req:
            bot.send_message(message.chat.id, SOURCE.getText('notWithdrawRequests', language))
        for i in req:
            # payBtn = types.InlineKeyboardButton(SOURCE.getText('payBtn', language))
            completeBtn = types.InlineKeyboardButton(SOURCE.getText('completeWithdrawBtn', language),
                                                     callback_data=SOURCE.withdraw_complete + '|' + str(i[0]))
            markup = types.InlineKeyboardMarkup().add(completeBtn)
            bot.send_message(message.chat.id,
                             str(SOURCE.getText('moneyRequestTemplate', language).format(username=i[1],
                                                                                         money=i[2],
                                                                                         link=str(i[3]))),
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
    if db.isBan(message.chat.id):
        bot.send_message(message.chat.id, SOURCE.getText('youBanned', db.getLanguage(message.chat.id)))
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
            bot.send_message(message.chat.id, SOURCE.getText('howCreateTaskText', language))
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

            def getCount(m):
                try:
                    count = int(m.text)
                except:
                    bot.send_message(m.chat.id, SOURCE.getText('incorrect', language))
                    return

                bot.send_message(m.chat.id, SOURCE.getText('newTaskText', language))
                bot.register_next_step_handler(m, getPrice, count)

            bot.send_message(message.chat.id, SOURCE.getText('getTaskCount', language))
            bot.register_next_step_handler(message, getCount)

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
            tasks = db.getTasks(id=message.chat.id, role=db.getRole(message.chat.id))

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
    if message.text == SOURCE.getText('chancelWithdrawBtn', db.getLanguage(message.chat.id)):
        mainMenuView(message)
        return
    if message.text == SOURCE.getText('allMoneyBtn', db.getLanguage(message.chat.id)):
        value = db.getBalance(message.chat.id)
    else:
        value = message.text
    if db.isHaveRequest(message.chat.id):
        bot.send_message(message.chat.id, SOURCE.getText('getLinks', db.getLanguage(message.chat.id)))
        bot.register_next_step_handler(message, db.setHowMuchMoney, value)

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
        bot.send_message(message.chat.id, SOURCE.getText('howUseReferral', language))
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
    markup = types.InlineKeyboardMarkup()

    checkTopupBtn = types.InlineKeyboardButton(SOURCE.getText('checkTopupBtn', db.getLanguage(message.chat.id)),
                                               callback_data=SOURCE.check_payment)
    markup.add(checkTopupBtn)
    if price < SOURCE.min_money:
        bot.send_message(message.chat.id,
                         str(SOURCE.getText('minMoneyText',
                                            db.getLanguage(message.chat.id)).format(min_money=SOURCE.min_money)))
        return
    bot.send_message(message.chat.id, ton.get_invoice(message, price), reply_markup=markup)


def getPrice(message, count):
    text = message.text

    bot.send_message(message.chat.id, SOURCE.getText('getPriceText', db.getLanguage(message.chat.id)))
    bot.register_next_step_handler(message, db.newTask, text, count)


def deleteMessage(chat_id, message_id):
    bot.delete_message(chat_id, message_id)


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
            bot.send_message(callback.message.chat.id,
                             SOURCE.getText('youCanContinueRegister', SOURCE.default_language))
        return

    language = db.getLanguage(callback.message.chat.id)

    if SOURCE.check_payment == callback.data:
        try:
            bot.send_message(callback.message.chat.id, ton.check_payment(callback.message))
        except Exception as e:
            print(e)
    if SOURCE.unban in callback.data:
        userId = callback.data[callback.data.find('|') + 1:]
        db.unbanStatus(userId)
        bot.send_message(callback.message.chat.id, SOURCE.getText('userUnbanned', language))

    if SOURCE.ban in callback.data:
        userId = callback.data[callback.data.find('|') + 1:]
        db.banStatus(userId)
        bot.send_message(callback.message.chat.id, SOURCE.getText('userBanned', language))
    if SOURCE.set_balance_command in callback.data:
        def setBalance(m, id):
            value = m.text
            bot.send_message(m.chat.id, SOURCE.getText('setBalanceComplete', language))
            db.setBalance(id, value)

        bot.send_message(callback.message.chat.id,
                         SOURCE.getText('setBalanceText', language))
        bot.register_next_step_handler(callback.message, setBalance, callback.data[callback.data.find('|') + 1:])
    if SOURCE.withdraw_complete in callback.data:
        userId = callback.data[callback.data.find('|') + 1:]
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        db.setBalance(userId, str(-1 * db.getMoneyFromRequest(userId)))
        db.deleteMoneyRequest(userId)
        bot.send_message(userId, SOURCE.getText('moneyWithdrawComplete', db.getLanguage(userId)))
        bot.send_message(callback.message.chat.id, SOURCE.getText('moneyWithdrawCompleteAdminText', language))
    if SOURCE.ruChange == callback.data:
        db.setLanguage(callback.message.chat.id, SOURCE.ruChange)
        bot.send_message(callback.message.chat.id, SOURCE.getText('changeLanguageComplete', language))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        mainMenuView(callback.message)

    if SOURCE.enChange == callback.data:
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
        executorID = callback.data[callback.data.find('|') + 1:callback.data.rfind('|')]
        taskId = callback.data[callback.data.rfind('|') + 1:]
        db.setRating(executorID, -1)
        db.setTaskActivity(taskId, SOURCE.db_True)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(executorID, SOURCE.getText('yourReportCancel', db.getLanguage(executorID)))

    if SOURCE.acceptReport in callback.data:
        executorID = callback.data[callback.data.find('|') + 1:callback.data.rfind('|')]
        taskId = callback.data[callback.data.rfind('|') + 1:]
        db.setRating(executorID, 1)
        db.setTaskCount(taskId)

        db.setBalance(executorID, db.getPrice(taskId))
        db.setBalance(callback.message.chat.id, -db.getPrice(taskId))
        db.setCompleteTasks(executorID)
        if db.getTaskCount(taskId) <= 0:
            db.setTaskActivity(taskId, False)
            db.deleteTask(taskId)

        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(executorID, SOURCE.getText('yourReportAccept', db.getLanguage(executorID)))


@bot.message_handler(content_types=['photo'])
def get_photo(message, employerID=None, taskId=None):
    if employerID is None or taskId is None:
        return

    nextMessage = 0
    while True:
        try:
            bot.copy_message(chat_id=employerID, from_chat_id=message.chat.id,
                             message_id=message.message_id + nextMessage)
            nextMessage += 1
        except:
            break

    # bot.send_message(employerID, message)
    # db.setTaskActivity(taskId, SOURCE.db_False)
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
    bot.send_message(message.chat.id, SOURCE.getText('yourReportRejected', db.getLanguage(message.chat.id)))


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0, timeout=0)
