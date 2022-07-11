#!/usr/bin/env python3

import telebot
import configparser

config = configparser.ConfigParser()
config.read_file(open('./token.config', mode='r'))
token = config.get('config', 'token')

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()