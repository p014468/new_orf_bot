import json
import os
import logging
import traceback
import re
import operator
import random
import requests
from bs4 import BeautifulSoup

from config import TOKEN, ADMIN_ID, CHANNEL_ID
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, BaseFilter, CallbackQueryHandler
#from telegram.ext import MessageFilter
from emoji import emojize

#ini
BOT_USERNAME = '@news_orf_bot'

#service functions

def isAdmin(id):
    return id in ADMIN_ID

#class startFilter(MessageFilter):
class startFilter(BaseFilter):
    def filter(self, message):
        txt = message.text.replace(BOT_USERNAME, '')
        return txt == '/start' and message.forward_from == None and isAdmin(message.from_user.id)

start_filter = startFilter()

'''
class fetchFilter(MessageFilter):
    def filter(self, message):
        txt = message.text.replace(BOT_USERNAME, '')
        return txt == '/fetch'

fetch_filter = fetchFilter()
'''
class fetchFilter(BaseFilter):
#class fetchFilter(MessageFilter):
    def filter(self, message):
        return len(re.findall(r'^/fetch (-?\d+)$', message.text)) != 0

fetch_filter = fetchFilter()


def start(update, context):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    msg = update.message.text
    try:
        context.bot.send_message(chat_id, 'test after looong pause.')
    except Exception:
        logging.error(traceback.format_exc())

# fetch news as function

'''
def fetchNews(update, context):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    msg = update.message.text
    try:
        orf = requests.get('https://news.orf.at')
        orf_html = BeautifulSoup(orf.text, 'html.parser')
        orf_html_a_tags = orf_html.find_all('a')
        orf_links = []
        for i in range(len(orf_html_a_tags)):
            if 'https://orf.at/stories/' in orf_html_a_tags[i].get('href') and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/impressum-nachrichtenagenturen/' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/impressum/' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/datenschutz' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/darstellung':
                orf_links.append(orf_html_a_tags[i].get('href'))
        orf_random_news = random.choice(orf_links)
        context.bot.send_message(CHANNEL_ID, orf_random_news, parse_mode = 'HTML')
    except Exception:
        logging.error(traceback.format_exc())
'''


def fetchNews(context):
    orf = requests.get('https://news.orf.at')
    orf_html = BeautifulSoup(orf.text, 'html.parser')
    orf_html_a_tags = orf_html.find_all('a')
    orf_links = []
    for i in range(len(orf_html_a_tags)):
        if 'https://orf.at/stories/' in orf_html_a_tags[i].get('href') and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/impressum-nachrichtenagenturen/' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/impressum/' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/datenschutz' and orf_html_a_tags[i].get('href') != 'https://orf.at/stories/darstellung':
            orf_links.append(orf_html_a_tags[i].get('href'))
    orf_random_news = random.choice(orf_links)
    context.bot.send_message(chat_id = context.job.context, text = orf_random_news)


def sendNews(update, context):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    msg = update.message.text
    intrvl = re.search(r'^/fetch (-?\d+)$', msg).group(1)
    #context.bot.send_message(chat_id, intrvl)
    try:
        if isAdmin(user_id):
            if int(intrvl) >= 0:
                print('starting with interval of ' + str(intrvl) + ' seconds...')
                context.bot.send_message(chat_id = chat_id, text = 'Sending messages to the channel https://t.me/news_orf once in a ' + str(intrvl) + ' second(s).', parse_mode = 'HTML')
                context.job_queue.run_repeating(fetchNews, interval=int(intrvl), first=0, context = CHANNEL_ID, name='News')
                print(context.job_queue.jobs())
            elif int(intrvl) < 0:
                print('...stopping')
                context.bot.send_message(chat_id = chat_id, text = 'Stopped sending messages to the channel https://t.me/news_orf.', parse_mode = 'HTML')
                context.job_queue.jobs()[0].schedule_removal()
                print(context.job_queue.jobs())
            else:
                pass
    except Exception:
        logging.error(traceback.format_exc())

def main():

    updater = Updater(token=TOKEN, use_context = True)
    dispatcher = updater.dispatcher
    #jobs = updater.job_queue

    #jobs.run_once(test_job, 10)
    #jobs.run_repeating(go, 5,)

    start_handler = MessageHandler(start_filter, start)
    dispatcher.add_handler(start_handler)

    fetch_handler = MessageHandler(fetch_filter, sendNews)
    dispatcher.add_handler(fetch_handler)

    updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()
