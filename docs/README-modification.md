# Игра в телеграм-боте "Быки и коровы"

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
Команда для бота может быть создана при помощи декоратора `@bot.message_handler` и аргументом `commands=['command']. В ответе на команду старта а так же на команду помощи будет содержаться приветственное сообщение и правила игры. После получения ответа у пользователя будет доступна кнопка с командой "/newgame"
```python
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('/newgame'))
    
    bot.send_message(
        message.chat.id,
        "🐂🐄 Игра 'Быки и коровы'!\n\n"
        "Я загадал 4-значное число с неповторяющимися цифрами.\n"
        "Твоя задача - угадать его.\n\n"
        "• Бык - правильная цифра на правильном месте\n"
        "• Корова - правильная цифра на неправильном месте\n\n"
        "Нажми /newgame чтобы начать!",
        reply_markup=markup
    )
```

#### 3.3. Команда начала игры
Когда пользователь выполняет команду начала игры ("/newgame"), бот генерирует случайное число из четырех уникальных цифр и запоминает его. Генерация числа будет вынесена в отдельную функцию
```python
import random

games = {}

def generate_secret_number():
    digits = list('0123456789')  # Все возможные цифры
    random.shuffle(digits)  # Перемешиваем
    # Берем первые 4 цифры, исключая варианты, начинающиеся с 0
    while True:
        secret = ''.join(digits[:4])
        if secret[0] != '0':
            return secret
        random.shuffle(digits)

@bot.message_handler(commands=['newgame'])
def new_game(message):
    chat_id = message.chat.id
    games[chat_id] = {
        'secret': generate_secret_number(),
        'attempts': 0
    }
    print(f"New game for {chat_id}, secret: {games[chat_id]['secret']}")  # Для отладки
    bot.send_message(chat_id, "🔢 Я загадал новое 4-значное число! Попробуй угадать:")
```

#### 3.4. Обработка попытки угадать
Когда пользователь делает попытку угадать загаданное число, хэндлер обрабатывает сообщение и совершает необходимые действия в зависимости от того, насколько пользователь был близок к верному числу. Если число не было угадано, ответ формируется на основе правил: описание результата попытки в виде количества быков и коров. Если пользователь угадал число, ему выписываются поздравления и предложение сыграть еще раз
```python
@bot.message_handler(func=lambda message: True)
def handle_guess(message):
    chat_id = message.chat.id
    user_input = message.text.strip()
    
    # Если игры нет - предлагаем начать
    if chat_id not in games:
        bot.send_message(chat_id, "Нажми /newgame чтобы начать игру!")
        return
    
    # Проверка ввода
    if not (user_input.isdigit() and len(user_input) == 4 and len(set(user_input)) == 4):
        bot.send_message(chat_id, "❌ Нужно ввести 4-значное число с разными цифрами!")
        return
    
    if user_input[0] == '0':
        bot.send_message(chat_id, "❌ Число не может начинаться с 0!")
        return
    
    # Получаем данные игры
    secret = games[chat_id]['secret']
    games[chat_id]['attempts'] += 1
    
    # Считаем быков и коров
    bulls = sum(1 for i in range(4) if user_input[i] == secret[i])
    cows = sum(1 for d in user_input if d in secret) - bulls
    
    # Формируем ответ
    attempt_text = f"Попытка #{games[chat_id]['attempts']}:\n"
    result_text = f"Твой вариант: {user_input}\nРезультат: {bulls} бык(а), {cows} коров(ы)\n"
    
    # Проверка победы
    if bulls == 4:
        win_text = (f"🎉 Поздравляю! Ты угадал число {secret} "
                   f"за {games[chat_id]['attempts']} попыток!\n\n"
                   "Нажми /newgame для новой игры.")
        del games[chat_id]  # Завершаем игру
        bot.send_message(chat_id, attempt_text + result_text + win_text)
    else:
        bot.send_message(chat_id, attempt_text + result_text + "\nПопробуй ещё раз!")
```

### 4. Запуск
Запуск производится двойным нажатием на файл .py, который мы создали, либо же выполнением команды в командной строке:
```bash
python modification.py
```

### 5. Работа бота
Бот в рабочем состоянии способен играть с пользователем в мини-игру "Быки и коровы", где загадывает число бот, а отгадывает его пользователь
Пример работы запущенного бота:
![Sample of the bot working](https://sun9-23.userapi.com/impg/cWvO2MBSMIYt9pPCyE4wZdruxJdjfn0aP-rx3A/4xFP-vLQTGE.jpg?size=1179x1567&quality=95&sign=ae59504cc796a75e263dc62d3acc6ed5&type=album)