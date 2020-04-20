import redis
from telegram_bot import REDIS_URL, REDIS_PORT, REDIS_PASSWORD

redis_base = redis.Redis(host=REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD, charset="utf-8", decode_responses=True, )
# redis_base.set(123, '1')
question = redis_base.get(123)
answer = redis_base.get(question)
print(answer)
