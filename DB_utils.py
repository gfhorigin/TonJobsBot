import sqlite3
import Viewer as view
import SOURCE


def isNew(id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT id FROM users WHERE id = ?''', [id, ]).fetchone()

    con.commit()
    con.close()
    if req is None:
        return True
    return False


def CreateTable():
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users( id INTEGER PRIMARY KEY,
                                                    status TEXT,
                                                    rating INTEGER DEFAULT 0,
                                                    balance INTEGER DEFAULT 0,
                                                    language TEXT
                                                    ) ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tasks( taskId INTEGER PRIMARY KEY,
                                                     taskText TEXT,
                                                     executorId INTEGER,
                                                     employerId INTEGER,
                                                     isActive TEXT) ''')

    con.commit()
    con.close()


def newTask(m):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    text = m.text
    employerId = m.chat.id

    taskId = cur.execute('''SELECT taskId FROM tasks''').fetchall()[-1][0] + 1

    cur.execute('''INSERT INTO tasks(taskId, taskText, employerId, isActive) VALUES(?, ?, ?, ?) ''', [taskId,
                                                                                                      text,
                                                                                                       employerId,
                                                                                                       "TRUE", ])

    con.commit()
    con.close()
    view.anotherMessage(m.chat.id,SOURCE.getText('newTaskCreated',getLanguage(m.chat.id)))

def NewUser(m):
    id = m.chat.id
    language = m.from_user.language_code

    if language not in SOURCE.languages:
        language = 'ru'
    if m.text == SOURCE.getText('employer', language):
        role = SOURCE.employer
    elif m.text == SOURCE.getText('executor', language):
        role = SOURCE.executor
    else:
        view.anotherMessage(m.chat.id, "вы ввели некоректную роль")
        return

    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''INSERT INTO users(id, status, language) VALUES(?, ?, ?) ''', [id, role, language, ])

    con.commit()
    con.close()
    view.mainMenuView(m)


def getLanguage(id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT language FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getTasks(id=None):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()
    if id is None:
        req = cur.execute('''SELECT taskText, taskId FROM tasks WHERE isActive = ?''', ['TRUE', ]).fetchall()
    else:
        req = cur.execute('''SELECT taskText, taskId FROM tasks WHERE employerId = ?''', [id, ]).fetchall()
    con.commit()
    con.close()

    return req


def getTask(taskId):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT taskText FROM tasks WHERE taskId = ?''', [taskId, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def getRole(id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT status FROM users WHERE id = ?''', [id, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def deleteTask(taskId):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''DELETE FROM tasks WHERE taskId = ?''', [taskId, ])

    con.commit()
    con.close()

    return


def getEmployerId(taskId):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT employerId FROM tasks WHERE taskId = ?''', [taskId, ]).fetchone()[0]

    con.commit()
    con.close()

    return req


def setTaskActivity(taskId, value):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''UPDATE tasks SET isActive = ? WHERE taskId = ?''', [value, taskId, ])

    con.commit()
    con.close()


def setRating(id, value):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''UPDATE users SET rating = rating+? WHERE id = ?''', [value, id, ])

    con.commit()
    con.close()

def setTaskExecutorId(taskId,id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''UPDATE tasks SET executorId = ? WHERE taskId = ?''', [id, taskId, ])

    con.commit()
    con.close()




