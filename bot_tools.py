import logging
import re
import random


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


def get_random_question_and_answer(questions_and_answers):
    random_index = random.randint(0, len(questions_and_answers))
    return questions_and_answers[random_index]
