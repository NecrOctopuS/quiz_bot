import logging
import os
import re
import random

import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
FILENAME = os.environ['FILENAME']


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_questions_and_answers_from_file(filename):
    with open(filename, "r", encoding='KOI8-R') as my_file:
        file_contents = my_file.read()

    texts = file_contents.split('\n\n')
    questions_and_answers = []
    for text in texts:
        if 'Вопрос' in text:
            question = re.sub(r'(Вопрос \d*:)', '', text).strip('\n')
        elif 'Ответ' in text:
            answer = re.sub(r'(Ответ:)', '', text).strip('\n')
            questions_and_answers.append({
                'Вопрос': question,
                'Ответ': answer,
            })
    return questions_and_answers


def shorten_answer(answer):
    return re.sub(r'(\(|\.).*', '', answer).strip()


def get_random_question_and_answer(questions_and_answers):
    random_index = random.randint(0, len(questions_and_answers))
    return questions_and_answers[random_index]


def get_question_for_new_request(chat_id, connection=None):
    question, answer = get_random_question_and_answer(get_questions_and_answers_from_file(FILENAME)).values()
    if connection:
        connection.hset(chat_id, question, answer)
        return question
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    redis_base.hset(chat_id, question, answer)
    redis_base.close()
    return question


def get_answer_for_last_question(chat_id, connection=None):
    if connection:
        return list(connection.hgetall(chat_id).values())[0]
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    answer = list(redis_base.hgetall(chat_id).values())[0]
    redis_base.close()
    return answer
