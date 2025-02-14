import sqlite3
import Viewer as view
import SOURCE


def isNew(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT id FROM users WHERE id = ?''', [id, ]).fetchone()

    con.commit()
    con.close()
    if req is None:
        return True
    return False


def isHaveRequest(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT userId FROM money_requests WHERE userId = ?''', [id, ]).fetchone()

    con.commit()
    con.close()
    if req is None:
        return False
    return True


def CreateTable():
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users( id INTEGER PRIMARY KEY,
                                                    username TEXT,
                                                    status TEXT,
                                                    completeTasks DEFAULT 0,
                                                    createTasks DEFAULT 0,
                                                    rating INTEGER DEFAULT 0,
                                                    balance INTEGER DEFAULT 0,
                                                    language TEXT,
                                                    referral INTEGER DEFAULT 0
                                                    ) ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tasks( taskId INTEGER PRIMARY KEY,
                                                     taskText TEXT,
                                                     executorId INTEGER,
                                                     employerId INTEGER,
                                                     isActive TEXT,
                                                     price INTEGER) ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS money_requests( userId INTEGER PRIMARY KEY,
                                                         username TEXT,
                                                         money INTEGER,
                                                         walletLink TEXT) ''')

    con.commit()
    con.close()


def newMoneyRequests(m, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()
    id = m.chat.id
    link = m.text
    try:
        print(value)
        money = float(value.replace(',', '.'))
    except:
        view.anotherMessage(id, SOURCE.getText('noIntPrice', getLanguage(id)))
        con.commit()
        con.close()
        view.mainMenuView(m)
        return
    if money > getBalance(id):
        view.anotherMessage(id, SOURCE.getText('notEnoughMoneyWithdraw', getLanguage(id)))
        con.commit()
        con.close()
        view.mainMenuView(m)
        return
    if money < SOURCE.min_money:
        view.anotherMessage(id,
                            str(SOURCE.getText('minMoneyText',
                                               getLanguage(id)).format(min_money=SOURCE.min_money)))
        con.commit()
        con.close()
        view.mainMenuView(m)
        return
    if SOURCE.correct_wallet_link not in link:
        con.commit()
        con.close()
        view.anotherMessage(id, SOURCE.getText('notCorrectLink', getLanguage(id)))
        view.mainMenuView(m)
        return
    username = getUsername(id)
    req = cur.execute('''INSERT INTO money_requests(money, userId, walletLink, username) VALUES(?, ?, ?, ?)''',
                      [money, id, link, username])

    con.commit()
    con.close()
    view.anotherMessage(id, SOURCE.getText('withdrawRequestComplete', getLanguage(id)))
    view.mainMenuView(m)


def newAdmin(m):
    id = m.chat.id
    language = m.from_user.language_code
    username = m.from_user.username
    if language not in SOURCE.languages:
        language = 'ru'

    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''INSERT INTO users(id, status, language, username) VALUES(?, ?, ?, ?) ''',
                [id, 'admin', language, username])

    con.commit()
    con.close()
    view.adminPanelView(m)


def newTask(m, text):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()
    try:

        price = float(m.text.replace(',', '.'))

    except:
        view.anotherMessage(m.chat.id, SOURCE.getText('noIntPrice', SOURCE.default_language))
        con.commit()
        con.close()
        return
    if getBalance(m.chat.id) < getAllTasksPrice(m.chat.id) + price:
        view.anotherMessage(m.chat.id, SOURCE.getText('notEnoughMoney', SOURCE.default_language))
        con.commit()
        con.close()
        return

    employerId = m.chat.id
    try:
        taskId = cur.execute('''SELECT taskId FROM tasks''').fetchall()[-1][0] + 1
    except:
        taskId = 1
    cur.execute('''INSERT INTO tasks(taskId, taskText, employerId, isActive, price) VALUES(?, ?, ?, ?, ?) ''', [taskId,
                                                                                                                text,
                                                                                                                employerId,
                                                                                                                SOURCE.db_True,
                                                                                                                price])

    con.commit()
    con.close()
    view.anotherMessage(m.chat.id, SOURCE.getText('newTaskCreated', getLanguage(m.chat.id)))


def NewUser(m):
    id = m.chat.id
    language = m.from_user.language_code
    username = m.from_user.username
    if language not in SOURCE.languages or language is None:
        language = SOURCE.default_language
    if m.text == SOURCE.getText('employer',  SOURCE.default_language):
        role = SOURCE.employer
    elif m.text == SOURCE.getText('executor',  SOURCE.default_language):
        role = SOURCE.executor
    else:
        view.anotherMessage(m.chat.id, SOURCE.getText('uncorrectedRole', SOURCE.default_language))

        return

    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''INSERT INTO users(id, status, language, username) VALUES(?, ?, ?, ?) ''',
                [id, role, language, username])

    con.commit()
    con.close()
    view.mainMenuView(m)


def getAllTasksPrice(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT price FROM tasks WHERE employerId = ?''', [id, ]).fetchall()

    con.commit()
    con.close()

    prices = 0
    for i in req:
        prices += i[0]
    return prices


def getStatistic():
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    employers = len(cur.execute('''SELECT id FROM users WHERE status = ?''', [SOURCE.employer, ]).fetchall())
    executors = len(cur.execute('''SELECT id FROM users WHERE status = ?''', [SOURCE.executor, ]).fetchall())
    tasksActiv = len(cur.execute('''SELECT taskId FROM tasks WHERE isActive = ?''', [SOURCE.db_True, ]).fetchall())

    con.commit()
    con.close()
    return [employers, executors, tasksActiv]


def getUsers():
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT id FROM users ''').fetchall()

    con.commit()
    con.close()

    return req


def getLanguage(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT language FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getTasks(id=None):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()
    if id is None:
        req = cur.execute('''SELECT taskText, taskId FROM tasks WHERE isActive = ?''', [SOURCE.db_True, ]).fetchall()
    else:
        req = cur.execute('''SELECT taskText, taskId FROM tasks WHERE employerId = ?''', [id, ]).fetchall()
    con.commit()
    con.close()

    return req


def getUsername(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT username FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getTask(taskId):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT taskText FROM tasks WHERE taskId = ?''', [taskId, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getMoneyFromRequest(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT money FROM money_requests WHERE userId = ? ''',[id,]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getMoneyRequests():
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT * FROM money_requests ''').fetchall()

    con.commit()
    con.close()

    return req


def getPercents(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    ref = cur.execute('''SELECT referral FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    if ref > 0:
        return 0.95
    return 0.85


def getRole(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT status FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getPrice(taskId):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT price FROM tasks WHERE taskId = ?''', [taskId, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getBalance(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT balance FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getHowMuchMoney(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT money FROM money_requests WHERE userId = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getCreateTasks(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT createTasks FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getBalance(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT balance  FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getCompleteTasks(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT completeTasks FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getEmployerId(taskId):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    req = cur.execute('''SELECT employerId FROM tasks WHERE taskId = ?''', [taskId, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def setTaskActivity(taskId, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE tasks SET isActive = ? WHERE taskId = ?''', [value, taskId, ])

    con.commit()
    con.close()


def setRating(id, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE users SET rating = rating+? WHERE id = ?''', [value, id, ])

    con.commit()
    con.close()


def setTaskExecutorId(taskId, id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE tasks SET executorId = ? WHERE taskId = ?''', [id, taskId, ])

    con.commit()
    con.close()


def setBalance(id, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    try:
        price = float(value.replace(',', '.'))
    except:
        view.anotherMessage(value, SOURCE.getText('noIntPrice', getLanguage(id)))
        con.commit()
        con.close()
        return

    cur.execute('''UPDATE users SET balance = balance  + ? WHERE id = ?''', [price, id, ])

    con.commit()
    con.close()


def setCompleteTasks(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE users SET completeTasks = completeTasks + 1 WHERE id = ?''', [id, ])

    con.commit()
    con.close()


def setHowMuchMoney(id, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    try:
        money = float(value.replace(',', '.'))
    except:
        view.anotherMessage(id, SOURCE.getText('noIntPrice', getLanguage(id)))
        con.commit()
        con.close()
        return
    if money > getBalance(id):
        view.anotherMessage(id, SOURCE.getText('notEnoughMoneyWithdraw', getLanguage(id)))
        con.commit()
        con.close()
        return
    if money < SOURCE.min_money:
        view.anotherMessage(id,
                            str(SOURCE.getText('minMoneyText',
                                               getLanguage(id)).format(min_money=SOURCE.min_money)))
        con.commit()
        con.close()
        return
    req = cur.execute('''UPDATE money_requests SET money = ? WHERE userId = ?''', [money, id, ])

    con.commit()
    con.close()
    view.anotherMessage(id, SOURCE.getText('withdrawRequestComplete', getLanguage(id)))


def setCreateTasks(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE users SET createTasks = createTasks+1 WHERE id = ?''', [id, ])

    con.commit()
    con.close()


def setLanguage(id, value):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE users SET language = ? WHERE id = ?''', [value, id, ])

    con.commit()
    con.close()


def setReferral(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''UPDATE users SET referral = referral+1 WHERE id = ?''', [id, ])

    con.commit()
    con.close()


def deleteTask(taskId):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''DELETE FROM tasks WHERE taskId = ?''', [taskId, ])

    con.commit()
    con.close()

    return


def deleteMoneyRequest(id):
    con = sqlite3.connect(SOURCE.data_base_name)
    cur = con.cursor()

    cur.execute('''DELETE FROM money_requests WHERE userId = ?''', [id, ])

    con.commit()
    con.close()

    return
