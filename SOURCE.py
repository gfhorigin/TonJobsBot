import configparser


def getText(value: str, lg: str):
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("TEXTS.ini",  encoding="utf-8")
    return config[lg][value]  # читаем конфиг


executor = "executor"
employer = "employer"
languages = ['ru', 'en']