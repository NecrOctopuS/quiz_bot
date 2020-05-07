import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import redis
import logging
import telegram
from bot_tools import TelegramLogsHandler, get_random_question_and_answer, \
    get_questions_and_answers_from_file, shorten_answer

load_dotenv()
VK_TOKEN = os.environ['VK_TOKEN']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_ID = os.environ['TELEGRAM_ID']
REDIS_URL = os.environ['REDIS_URL']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
FILENAME = os.environ['FILENAME']

logger = logging.getLogger('telegram_logger')


def send_keyboard(event, vk_api):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
        message='Приветствую, это бот для викторины. Для начала викторины, нажмите кнопку Новый вопрос'
    )


def handle_new_question_request(event, vk_api):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = event.user_id
    question, answer = get_random_question_and_answer(get_questions_and_answers_from_file(FILENAME)).values()
    redis_base.set(chat_id, question)
    redis_base.set(question, answer)
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=question)


def handle_give_up(event, vk_api):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = event.user_id
    question = redis_base.get(chat_id)
    answer = redis_base.get(question)
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=f'Правильный ответ:{answer}')
    handle_new_question_request(event, vk_api)


def handle_solution_attempt(event, vk_api):
    redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD,
                             charset="utf-8", decode_responses=True)
    chat_id = event.user_id
    question = redis_base.get(chat_id)
    answer = redis_base.get(question)
    if shorten_answer(answer) in event.text:
        text = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
    else:
        text = "Неправильно... Попробуешь ещё раз?"
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=text)


if __name__ == "__main__":
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot, TELEGRAM_ID))
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'start':
                send_keyboard(event, vk_api)
            elif event.text == "Сдаться":
                handle_give_up(event, vk_api)
            elif event.text == "Новый вопрос":
                handle_new_question_request(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)


