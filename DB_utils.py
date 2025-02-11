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

def getTasks(id = None):

    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()
    if id is None:
        req = cur.execute('''SELECT taskText FROM tasks WHERE isActive = ?''', ['TRUE', ]).fetchone()
    else:
        req = cur.execute('''SELECT taskText FROM tasks WHERE employerId = ?''', ['TRUE', ]).fetchone()
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


