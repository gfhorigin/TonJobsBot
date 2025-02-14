import requests
from dotenv import load_dotenv
import os
import DB_utils as db
import SOURCE
import Viewer as view

load_dotenv()
API_TOKEN = os.getenv('TON_TOKEN')

invoices = {}


# создание ссылки для оплаты
def get_pay_link(amount):
    headers = {"Crypto-Pay-API-Token": API_TOKEN}
    data = {"asset": "TON", "amount": amount}
    response = requests.post('https://pay.crypt.bot/api/createInvoice', headers=headers, json=data)
    if response.ok:
        response_data = response.json()
        return response_data['result']['pay_url'], response_data['result']['invoice_id']
    return None, None


# узнавание инфы по статусу оплаты конкретного id заказа
def check_payment_status(invoice_id):
    headers = {
        "Crypto-Pay-API-Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post('https://pay.crypt.bot/api/getInvoices', headers=headers, json={})

    if response.ok:
        return response.json()
    else:

        return None


# создание формы для оплаты

def get_invoice(message, price):
    chat_id = message.chat.id
    pay_link, invoice_id = get_pay_link(str(price))
    language = db.getLanguage(chat_id)
    if pay_link and invoice_id:
        invoices[chat_id] = [invoice_id, price]
        view.anotherMessage(chat_id, pay_link)
        return SOURCE.getText('takeLinkToPay', language)

    else:
        return SOURCE.getText('createLinkError', language)


# проверка статуса оплаты

def check_payment(message):
    chat_id = message.chat.id
    invoice_id = invoices[chat_id][0]
    price = invoices[chat_id][1]
    payment_status = check_payment_status(invoice_id)
    language = db.getLanguage(chat_id)

    if not payment_status and payment_status.get('ok'):
        return SOURCE.getText('paymentRequestError', language)

    if not 'items' in payment_status['result']:
        return SOURCE.getText('statusPaymentError', language)

    invoice = next((inv for inv in payment_status['result']['items'] if str(inv['invoice_id']) == invoice_id),
                   None)
    if invoice:
        return SOURCE.getText('walletBalanceNotFoundText', language)

    status = invoice['status']

    if status != 'paid':
        return SOURCE.getText('paymentNotFoundText', language)

    db.setBalance(chat_id, price*db.getPercents(chat_id))
    return SOURCE.getText("paymentCompletedText", language)
    #  bot.send_message(chat_id, "Оплата прошла успешно!✅")


