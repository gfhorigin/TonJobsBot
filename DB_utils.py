import sqlite3

def CreateTable():
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users( id INTEGER PRIMARY KEY  ) ''')

    con.commit()
    con.close()


def NewUser(id):
    con = sqlite3.connect("TonJobsBot.db")
    cur = con.cursor()

    cur.execute('''INSERT INTO users(id) VALUES(?) ''', [id,])

    con.commit()
    con.close()