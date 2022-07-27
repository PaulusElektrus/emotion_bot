#!/usr/bin/python3

import telebot
from telebot import types
import time, threading, schedule, configparser

config = configparser.ConfigParser()
config.read_file(open('./token.config', mode='r'))
token = config.get('config', 'token')

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Servus :-)")

@bot.message_handler(commands=['hilfe'])
def send_welcome(message):
    bot.reply_to(message, "Nutze /erinnern und gib eine Anzahl von Minuten ein in der du erinnert werden möchtest.")

def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Wie geht es dir gerade?')
    markup = types.ReplyKeyboardMarkup()
    itembtna = types.KeyboardButton('1')
    itembtnv = types.KeyboardButton('2')
    itembtnc = types.KeyboardButton('3')
    itembtnd = types.KeyboardButton('4')
    itembtne = types.KeyboardButton('5')
    itembtnf = types.KeyboardButton('6')
    markup.row(itembtna, itembtnv, itembtnc)
    markup.row(itembtnd, itembtne, itembtnf)
    tb.send_message(chat_id, "Vergib eine Note für deine Selbstfürsorge:", reply_markup=markup)

@bot.message_handler(commands=['erinnern'])
def set_timer(message):
    args = message.text.split()
    if len(args) == 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).minutes.do(beep, message.chat.id).tag(message.chat.id)
        bot.reply_to(message, "Erinnerung gestellt auf ", sec, " Minuten :-)")
    else:
        bot.reply_to(message, 'Bitte im Format: /erinnern 5 (zum Beispiel)')


@bot.message_handler(commands=['stop'])
def unset_timer(message):
    schedule.clear(message.chat.id)
    bot.reply_to(message, "Erinnerung deaktiviert!")


bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
