from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import logging
import os
import telegram
import redis

from bot_tools import TelegramLogsHandler, get_random_question_and_answer, get_questions_and_answers_from_file

load_dotenv()
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_ID = os.environ['TELEGRAM_ID']
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']

logger = logging.getLogger('telegram_logger')


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def send_buttons(bot, chat_id):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет', ]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id,
                     text="Привет, я бот для викторин!",
                     reply_markup=reply_markup)


def send_question(bot, update, chat_id, redis_base):
    filename = "questions/1vs1200.txt"
    question, answer = get_random_question_and_answer(get_questions_and_answers_from_file(filename)).values()
    print(answer)
    redis_base.set(chat_id, question)
    redis_base.set(question, answer)
    update.message.reply_text(question)


def reply(bot, update):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    # text = ''
    chat_id = update.message.chat_id
    question = redis_base.get(chat_id)
    if question:
        answer = redis_base.get(question)
    if update.message.text == 'Новый вопрос':
        send_question(bot, update, chat_id, redis_base)
    elif update.message.text == answer:
        text = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
    elif not question:
        send_buttons(bot, chat_id)
    else:
        # send_buttons(bot, chat_id)
        text = "Неправильно... Попробуешь ещё раз?"
    update.message.reply_text(text)


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot, TELEGRAM_ID))
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, reply))
    dp.add_error_handler(log_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
