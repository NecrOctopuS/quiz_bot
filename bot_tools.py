import logging
import os
import re
import random


from dotenv import load_dotenv

load_dotenv()

FILENAME = os.environ['FILENAME']


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_texts_from_file(filename):
    with open(filename, "r", encoding='KOI8-R') as my_file:
        file_contents = my_file.read()

    return file_contents.split('\n\n')


def get_questions_and_answers_from_texts(texts):
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


def get_questions_and_answers_from_file(filename):
    texts = get_texts_from_file(filename)
    return get_questions_and_answers_from_texts(texts)


def shorten_answer(answer):
    return re.sub(r'(\(|\.).*', '', answer).strip()


def get_question_for_new_request(chat_id, connection):
    question, answer = random.choice(get_questions_and_answers_from_file(FILENAME)).values()
    connection.hset(chat_id, 'answer', answer)
    return question


def get_answer_for_last_question(chat_id, connection):
    return connection.hget(chat_id, 'answer')
