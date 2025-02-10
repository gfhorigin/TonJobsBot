import sqlite3

def isNew(id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    req = cur.execute('''SELECT id FROM users WHERE id = ?''', [id,]).fetchone()

    con.commit()
    con.close()
    if req is None:
        return True
    return False

def CreateTable():
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users( id INTEGER PRIMARY KEY,
                                                    status TEXT) ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tasks( taskId INTEGER PRIMARY KEY,
                                                     taskText TEXT,
                                                     executorId INTEGER,
                                                     employerId INTEGER) ''')

    con.commit()
    con.close()


def NewUser(m):
    id = m.chat.id
    role = m.text

    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''INSERT INTO users(id, status) VALUES(?, ?) ''', [id, role, ])

    con.commit()
    con.close()