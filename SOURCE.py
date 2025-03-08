import configparser


def getText(value: str, lg: str):
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("TEXTS.ini", encoding="utf-8")
    return config[lg][value]  # читаем конфиг


channels = ['@coinferrari', '@bid_coinn']
channels_url = ['https://t.me/coinferrari', 'https://t.me/Ton_jobsofficiall']
executor = "executor"
employer = "employer"
ban = 'ban'
unban = 'unBan'
languages = ['ru', 'en']
deleteCallback = "delete"
respondCallback = "respond"
closeReport = "closed"
acceptReport = "accept"
data_base_name = "./data/TonJobsBot.db"
ruChange = "ru"
enChange = "en"
db_True = "TRUE"
db_False = "FALSE"
admin = 'admin'
referral_url = "https://t.me/Ton_jobs_bot?start={user_id}"
chancel_mailing = "chancelMailing"
chancel_withdraw_balance = "chancelWithdraw"
correct_wallet_link = 'https://t.me/CryptoBot'
withdraw_complete = 'withdrawComplete'
min_money = 0.001
min_money_withdraw = 1
for_referral_money = 0.005
channel_check = 'channelCheck'
default_language = 'ru'
check_payment = 'checkPayment'
set_balance_command = 'setBalance'
