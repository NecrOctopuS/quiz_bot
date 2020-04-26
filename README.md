### Quiz bot

It is quiz bot for [Telegram](https://telegram.org/) and [VK](https://vk.com/).

 
### How to install

Then you need to deploy this project to [Heroku](https://heroku.com/)

On [Heroku](https://heroku.com/) you need create the app, and connect it to this project.

In Settings -> Config Vars you need add next variables

```text
TELEGRAM_TOKEN='4645646:asd4a6dadawee4da6d4s'
TELEGRAM_ID='123456789'
VK_TOKEN='7fe50745b17ebda65a722b03b884419409747760d218b360b4e11fdd83c6b32b3fca86f05a4f1d52029fe81'
REDIS_URL='redis-14376.c114.us-east-1-4.ec2.cloud.redislabs.com'
REDIS_PORT='14376'
REDIS_PASSWORD='N7UTfIcBNg11231231JaDvPCCLcIIn7g5vFECav'
```

`TELEGRAM_TOKEN` can be take it from [BotFather](https://telegram.me/BotFather) by type `/start`
`/newbot`.

`TELEGRAM_ID` can be take it from [userinfobot](https://telegram.me/userinfobot) by type `/start`.

`VK_TOKEN` can be taken from settings API for your group in [VK](https://vk.com/).

`REDIS_URL`, `REDIS_PORT`, `REDIS_PASSWORD` can be taken from [Redis](https://redislabs.com/)

`FILENAME` it is yours filename for question and answers, that you wont to use.

After that in Resources you need turn on bot.


### How to run

In telegram or vk you need to write to your bot any message.
Bot will answer you.

### Questions and answers

In file `FILENAME` your questions need to be in this structure:
```text
Вопрос 1:
Греческие слова эмЕра "день" и имЕрос "сладкий" похожи. Поэтому, вопреки
логике, у Сапфо эмерофОн - это ОН. Назовите ЕГО.

Ответ:
Соловей.
```


### Objective of the project

The code is written for educational purposes on the online course for web developers [dvmn.org](https://dvmn.org/).