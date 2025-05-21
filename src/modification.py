import random
import telebot
from telebot import types

# Токен вашего бота (получите у @BotFather)
TOKEN = '8074455480:AAFHZ7TD6jUkEPzFIyeQ2e6D387Wy48uBhQ'
bot = telebot.TeleBot(TOKEN)

games = {}

def generate_secret_number():
    """Генерирует 4-значное число с уникальными цифрами"""
    digits = list('0123456789')  # Все возможные цифры
    random.shuffle(digits)  # Перемешиваем
    # Берем первые 4 цифры, исключая варианты, начинающиеся с 0
    while True:
        secret = ''.join(digits[:4])
        if secret[0] != '0':
            return secret
        random.shuffle(digits)

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

@bot.message_handler(commands=['newgame'])
def new_game(message):
    chat_id = message.chat.id
    games[chat_id] = {
        'secret': generate_secret_number(),
        'attempts': 0
    }
    print(f"New game for {chat_id}, secret: {games[chat_id]['secret']}")  # Для отладки
    bot.send_message(chat_id, "🔢 Я загадал новое 4-значное число! Попробуй угадать:")

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


if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
