from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from dotenv import load_dotenv
import logging
import os
import telegram
import redis
from bot_tools import TelegramLogsHandler, get_random_question_and_answer, \
    get_questions_and_answers_from_file, shorten_answer

load_dotenv()
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_ID = os.environ['TELEGRAM_ID']
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
FILENAME = os.environ['FILENAME']
PREFIX = os.environ.get('TG_PREFIX', 'tg-')

logger = logging.getLogger('telegram_logger')
CHOOSING, ANSWER = range(2)


def start(bot, update):
    reply_keyboard = [['Новый вопрос', 'Сдаться', 'Мой счет']]
    update.message.reply_text('Приветствую, это бот для викторины. Для начала викторины, нажмите кнопку Новый вопрос',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return CHOOSING


def help(bot, update):
    update.message.reply_text('Help!')


def handle_new_question_request(bot, update):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = f'{PREFIX}{update.message.chat_id}'
    question, answer = get_random_question_and_answer(get_questions_and_answers_from_file(FILENAME)).values()
    redis_base.set(chat_id, question)
    redis_base.set(question, answer)
    update.message.reply_text(question)

    return ANSWER


def handle_solution_attempt(bot, update):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = f'{PREFIX}{update.message.chat_id}'
    question = redis_base.get(chat_id)
    answer = redis_base.get(question)
    if shorten_answer(answer) in update.message.text:
        text = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        update.message.reply_text(text)
        return CHOOSING
    else:
        text = "Неправильно... Попробуешь ещё раз?"
        update.message.reply_text(text)


def handle_give_up(bot, update):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = f'{PREFIX}{update.message.chat_id}'
    question = redis_base.get(chat_id)
    answer = redis_base.get(question)
    update.message.reply_text(f'Правильный ответ:{answer}')
    handle_new_question_request(bot, update)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('До свидания!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot, TELEGRAM_ID))
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Новый вопрос)$', handle_new_question_request),
                       RegexHandler('^(Сдаться)$', handle_give_up),
                       RegexHandler('^(Мой счет)$', handle_new_question_request)],

            ANSWER: [RegexHandler('^(Сдаться)$', handle_give_up),
                     MessageHandler(Filters.text, handle_solution_attempt)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(log_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
