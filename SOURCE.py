import configparser


def getText(value: str, lg: str):
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("TEXTS.ini", encoding="utf-8")
    return config[lg][value]  # читаем конфиг


channels = ['@coinferrari', '@bid_coinn']
channels_url = ['https://t.me/coinferrari', 'https://t.me/Ton_jobsofficiall']
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
referral_url = "https://t.me/steal_wilberies_bot?start={user_id}"
chancel_mailing = "chancelMailing"
chancel_withdraw_balance = "chancelWithdraw"
correct_wallet_link = 'https://t.me/CryptoBot'
withdraw_complete = 'withdrawComplete'
min_money = 0.1
channel_check = 'channelCheck'
default_language = 'ru'
