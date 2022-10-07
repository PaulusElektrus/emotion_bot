#!/usr/bin/python3

import time, threading, schedule, configparser, data

import telebot
from telebot import types

version = "2.0.2"

config = configparser.ConfigParser()
config.read_file(open('./token.config', mode='r'))
token = config.get('config', 'token')

commands = {
    'start': 'Begrüßung & Scan',
    'hilfe': 'Informationen zur Bedienung',
    'erinnern': 'Die Erinnerung starten',
    'auswertung': 'Auswertung der Selbstfürsorge',
    'stop': 'Aktuelle Aktion abbrechen bzw. die Erinnerung stoppen',
    'version': 'Zeigt die aktuelle Version des Bots und die Neuerungen an'
}

number_board = types.ReplyKeyboardMarkup(one_time_keyboard=True)
itembtna = types.KeyboardButton('1')
itembtnv = types.KeyboardButton('2')
itembtnc = types.KeyboardButton('3')
itembtnd = types.KeyboardButton('4')
itembtne = types.KeyboardButton('5')
itembtnf = types.KeyboardButton('6')
number_board.row(itembtna, itembtnv, itembtnc)
number_board.row(itembtnd, itembtne, itembtnf)

hideBoard = types.ReplyKeyboardRemove()


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


def beep(cid):
    bot.send_message(cid, "Vergib eine Note für deine Selbstfürsorge:", reply_markup=number_board)
    data.store_userStep(cid, 2)

def first_start():
    cids = data.get_all_users()
    for x in cids:
        cid = x[0]
        name = x[1]
        bot.send_message(cid, f"Hallo {name}, der Bot wurde neu gestartet - Version: {version} - weitere Infos unter /version")


bot = telebot.TeleBot(token)
bot.set_update_listener(listener)


# Start
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    username = m.from_user.username
    db_cid = data.get_user(cid)
    if cid != db_cid:
        userStep = 0
        user_data = [
            (cid, first_name, last_name, username, userStep)
        ]
        data.store_user(user_data)
        bot.send_message(cid, "Hallo " + first_name + ", lass mich dich scannen...")
        time.sleep(2)
        bot.send_message(cid, "Scan abgeschlossen.")
        command_help(m)
    else:
        bot.send_message(cid, "Du bist im System unter der Numer " + str(cid) + " bereits registriert.")


# Hilfe
@bot.message_handler(commands=['hilfe'])
def command_help(m):
    cid = m.chat.id
    help_text = "Die folgenden Optionen sind verfügbar: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)


# Auswertung
@bot.message_handler(commands=['auswertung'])
def auswertung(m):
    cid = m.chat.id
    bot.send_message(cid, "Auswertung gestartet...")
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)
    bot.send_message(cid, "Hihi Feature noch nicht implementiert ;-)")


# Erinnern lassen
@bot.message_handler(commands=['erinnern'])
def erinnern(m):
    cid = m.chat.id
    bot.send_message(cid, "In wie vielen Minuten soll ich dich erinnern?")
    data.store_userStep(cid, 1)


# Erinnerung einstellen
@bot.message_handler(func=lambda message: data.get_userstep(message.chat.id) == 1)
def set_timer(m):
    cid = m.chat.id
    text = m.text
    args = text.split()

    bot.send_chat_action(cid, 'typing')

    if len(args) == 1 and args[0].isdigit():
        sec = int(args[0])
        schedule.every(sec).minutes.do(beep, cid).tag(cid)
        bot.send_message(cid, "Erinnerung gestellt!")
        data.store_userStep(cid, 0)
        return
    if text == "/stop":
        bot.send_message(cid, "Aktion abgebrochen!")
        data.store_userStep(cid, 0)
        return
    else:
        bot.reply_to(m, 'Bitte nur die Anzahl der Minuten eingeben.')
        bot.send_message(m, 'Bitte erneut versuchen.')


# Selbstfürsorge Nummer
@bot.message_handler(func=lambda message: data.get_userstep(message.chat.id) == 2)
def sfn(m):
    cid = m.chat.id
    nummer = m.text
    if nummer.isdigit():
        bot.send_chat_action(cid, 'typing')
        bot.send_message(cid, "Wie geht es die gerade?", reply_markup=hideBoard)
        data.store_userStep(cid, 3)
        return
    if nummer == "/stop":
        unset_timer(m)
        data.store_userStep(cid, 0)
        return
    else:
        bot.send_message(cid, "Bitte vorgegebenes Keyboard benutzen!")
        beep(cid)


# Selbstfürsorge Text
@bot.message_handler(func=lambda message: data.get_userstep(message.chat.id) == 3)
def sft(m):
    cid = m.chat.id
    text = m.text
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)
    bot.send_message(cid, "Danke! Pass weiterhin auf dich auf!", reply_markup=hideBoard)
    data.store_userStep(cid, 0)


# Stop
@bot.message_handler(commands=['stop'])
def unset_timer(message):
    schedule.clear(message.chat.id)
    bot.send_message(message, "Erinnerung deaktiviert!")


# Version
@bot.message_handler(commands=['version'])
def version_info(m):
    cid = m.chat.id
    bot.send_message(cid, f"Version: {version}\nAktuelle Neuerungen: \n- BUGFIX: /stop kann nun in jedem Zustand verwendet werden\n- Neue Versions- und Neustartinfo")


# Standard Handler
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    bot.send_message(m.chat.id, "Ich verstehe \"" + m.text + "\"nicht. Bitte einmal /start ausführen und dann /hilfe eingeben.")


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    first_start()
    while True:
        schedule.run_pending()
        time.sleep(1)