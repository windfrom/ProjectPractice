# Создание телеграм-бота с функцией гороскопа

## Создание телеграм-бота с надлежащим функционалом
### 1. Создание бота через BotFather
Для того, чтобы телеграм-бот мог существовать внутри мессенджера, необходимо создать его оболочку внутри Telegram. Это можно сделать с помощью официального бота от Telegram, который являтся отправной точкой для всех ботов этого мессенджера:
1. Зайти в диалог **[BotFather](https://t.me/botfather)**
2. Нажать кнопку "Start";
3. Выполнить команду "/newbot";
4. Дать боту имя и тег;
После этого BotFather пришлет вам сообщение, содержащее токен для доступа к управлению только что созданным ботом посредством Telegram API.
Пример взаимодействия с BotFather:
![Sample of BotFather interaction](https://sun9-69.userapi.com/impg/qKXoITWuUWc-wFC9OVZDc8B36r20o4DTp1fVxg/c5K5KFQ24do.jpg?size=487x1673&quality=95&sign=0a74c5472d549948061037fcf642b24c&type=album)

### 2. Предварительная настройка среды разработки
Функционал для бота будет написан с помощью языка программирования Python и библиотеки telebot. Установка библиотеки (при уже установленном интерпретаторе Python) производится выполнением следующей команды в командной строке:
```bash
pip install pyTelegramBotAPI
```

### 3. Написание функционала бота
#### 3.1. Основа
Основу бота составляет инициализация его объекта с помощью токена и запуск бесконечного цикла его работы
```python
import telebot

# В переменную TOKEN вставляется токен, который вы ранее получили у BotFather
TOKEN = 'TOKEN'
bot = telebot.TeleBot(TOKEN)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
```

#### 3.2. Команда старта
Команда для бота может быть создана при помощи декоратора `@bot.message_handler` и аргументом `commands=['command']. В ответе на команду старта а так же на команду помощи будет содержаться приветственное сообщение. После получения ответа у пользователя будет доступна кнопка с командой "/newgame"
```python
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")
```

#### 3.3. Команда вычисления гороскопа
Когда пользователь выполняет команду гороскопа ("/horoscope"), бот спрашивает знак зодиака пользвателя и методом `register_next_step_handler` задает функцию-обработчика следующего ответа пользователя
```python
@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)
```

#### 3.4. Обработчик дня
Функция-обработчик следующего ответа пользователя будет принимать день, на который пользователь хочет непосредственно узнать свой гороскоп. В конце мы задаем функцию-обработчик для получения самого гороскопа
```python
def day_handler(message):
    sign = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, fetch_horoscope, sign.capitalize())
```

#### 3.5. Запрос гороскопа через Horoscope API
После того, как бот получил ответ на запросы знака зодиака и целевого дня, можно через Horoscope API узнать и сам гороскоп (реализуем посредством модуля requests, напрямую). Функцию запроса гороскопа через API и отправки ответа на запрос пользователю будут разделены
```python
import requests

def get_daily_horoscope(sign: str, day: str) -> dict:
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    return response.json()

def fetch_horoscope(message, sign):
    day = message.text
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\\n*Sign:* {sign}\\n*Day:* {data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
```
Если сделать вывод результа выполнения функции `get_daily_horoscope()`, можно увидеть, что ответ с сервера API приходит в следующем виде:
```json
{
   "data":{
      "date": "Dec 15, 2022",
      "horoscope_data": "Lie low during the day and try not to get caught up in the frivolous verbiage that dominates the waking hours. After sundown, feel free to speak your mind. You may notice that there is a sober tone and restrictive sensation today that leaves you feeling like you will never be able to break free from your current situation. Don't get caught in this negative mindset."
   },
   "status": 200,
   "success": true
}
```

### 4. Запуск
Запуск производится двойным нажатием на файл .py, который мы создали, либо же выполнением команды в командной строке:
```bash
python main.py
```

### 5. Работа бота
Бот в рабочем состоянии способен спрашивать у пользователя его знак зодиака, целевую дату и выдавать гороскоп на указанную дату по указанному знаку зодиака
Пример работы запущенного бота:
![Sample of the bot working](https://sun9-6.userapi.com/impg/vJeqB7SUpLwMxfD19L3GOQ6Q3KhVHsyYZNWvDw/3FO3-Ud-MCg.jpg?size=720x1445&quality=95&sign=cb86eaf05557336f178b075494fcaff5&type=album)