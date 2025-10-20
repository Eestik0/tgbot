import telebot
import webbrowser
import pyjokes
import random
import re

bot = telebot.TeleBot('hhhhh')

# настрій
moods = ["😇 ангел", "🙂 спокійна", "😏 грайлива", "😠 зла", "😈 сатана"]
current_mood = random.choice(moods)

def random_mood():
    global current_mood
    if random.random() < 0.2:  # 20% шанс змінити настрій
        current_mood = random.choice(moods)

# фрази для випадкових реакцій (~20)
random_phrases = [
    "Хмм, цікаво 🤔",
    "Моя сатанинська сторона каже 'ні' 😈",
    "Ангельська — 'так' 😇",
    "Я тут, слухаю 👂",
    "Що сталося, котику? 😸",
    "Га? Я задумалась...",
    "А я вже скучила 🥺",
    "Це жарт був? Бо я майже засміялась 😏",
    "Може, поясниш простіше?",
    "Скажи ще раз, але повільніше 😄",
    "О, це виглядає цікаво!",
    "Я почуваюся дивно сьогодні…",
    "Ха-ха, я майже засміялась 😅",
    "Мій настрій коливається від ангела до сатани 😈😇",
    "Ммм, не впевнена, чи це хороша ідея...",
    "Окей, я приймаю це до уваги!",
    "Хм, можливо, це секрет 🤫",
    "Я бачу, ти намагаєшся мене спантеличити 😏",
    "Ого, цікаво, що буде далі!",
    "Я просто тут, щоб мило посміхатися 🙂"
]

# Команди
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f'Привіт, {message.from_user.first_name}! Я — Неля {current_mood} 😄\n\n'
        'Команди:\n'
        '/help — допомога\n'
        '/site — відкрити сайт\n'
        '/menu — переглянути всі можливості\n'
        '/joke — розповісти жарт\n'
        '/power — випадкова потужність\n'
        '/chance — оцінити шанс\n'
        '/mood — показати мій настрій\n'
    )

@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id,
        '<b>Список команд:</b>\n'
        '/joke — жарт\n'
        '/power — потужність\n'
        '/chance — шанс\n'
        '/site — відкрити дуже цікавенький сайт\n'
        '/menu — показати меню\n'
        '/mood — показати настрій\n',
        parse_mode='html'
    )

@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id,
        'Мої можливості 🪄\n'
        '• Відповідаю на привітання\n'
        '• Даю випадкову "потужність" (/power)\n'
        '• Визначаю потужність по фото\n'
        '• Оцінюю шанс (/chance)\n'
        '• Розповідаю жарти (/joke)\n'
        '• Реагую на фрази користувача\n'
        '• Мій настрій змінюється від ангела 😇 до сатани 😈'
    )

@bot.message_handler(commands=['site', 'website'])
def site(message):
    webbrowser.open('https://pornhub.com')
    bot.send_message(message.chat.id, 'Відкриваю сайт 🌐')

@bot.message_handler(commands=['joke'])
def joke(message):
    joke_text = pyjokes.get_joke(language='en')
    bot.send_message(message.chat.id, f'😄 {joke_text}')

@bot.message_handler(commands=['power'])
def power(message):
    value = random.randint(-99, 100)
    bot.send_message(message.chat.id, f'Потужність цього — {value} ⚡')

@bot.message_handler(commands=['chance'])
def chance(message):
    percent = random.randint(0, 100)
    bot.send_message(message.chat.id, f'Ймовірність цього — {percent}% 🎲')

@bot.message_handler(commands=['mood'])
def show_mood(message):
    bot.send_message(message.chat.id, f'Мій настрій зараз: {current_mood}')

# Потужність по фото
@bot.message_handler(content_types=['photo'])
def photo_power(message):
    value = random.randint(-99, 100)
    bot.send_message(message.chat.id, f'Хмм… потужність цього на фото приблизно {value} ⚡')

# Реакції на повідомлення
@bot.message_handler(func=lambda m: True)
def talk(message):
    global current_mood
    text = message.text.lower()
    random_mood()  # іноді змінює настрій

    # Привітання
    if 'привіт' in text:
        bot.send_message(message.chat.id, f'Привіт, {message.from_user.first_name}! {current_mood}')
        return

    # Потужність, коли звертаються до Нелі
    if 'неля' in text:
        if 'жарт' in text or 'анекдот' in text:
            joke_text = pyjokes.get_joke(language='en')
            bot.send_message(message.chat.id, f'😄 {joke_text}')
            return
        if 'потужн' in text:
            value = random.randint(-99, 100)
            bot.send_message(message.chat.id, f'Потужність цього — {value} ⚡')
            return
        if re.search(r'шанс', text):
            percent = random.randint(0, 100)
            bot.send_message(message.chat.id, f'Я думаю, шанс цього {percent}% 😏')
            return
        # загальні відповіді Нелі
        responses = [
            'Я тут, слухаю 👂',
            'Що сталося, котику? 😸',
            'Га? Я задумалась...',
            'А я вже скучила 🥺',
            'Моя сатанинська сторона каже "ні" 😈',
            'Ангельська — "так" 😇'
        ]
        bot.send_message(message.chat.id, random.choice(responses))
        return

    # Дякую
    if 'дякую' in text:
        bot.send_message(message.chat.id, 'Будь ласка ❤️')
        return

    # Випадкові фрази з 30% шансом
    if random.random() < 0.3:
        bot.send_message(message.chat.id, random.choice(random_phrases))
        return

bot.infinity_polling()


