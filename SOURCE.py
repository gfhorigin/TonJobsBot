import configparser


def getText(value: str, lg: str):
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("TEXTS.ini", encoding="utf-8")
    return config[lg][value]  # читаем конфиг


executor = "executor"
employer = "employer"
languages = ['ru', 'en']
deleteCallback = "delete"
respondCallback = "respond"
closeReport = "closed"
acceptReport = "accept"
data_base_name = "TonJobsBot.db"
ruChange = "ru"
enChange = "en"
db_True = "TRUE"
db_False = "FALSE"

