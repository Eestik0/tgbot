import telebot
from telebot import types
import webbrowser
import pyjokes
import random
import re
import os
import requests
from openai import OpenAI

bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
# the newest OpenAI model is "gpt-4o" which works best for this use case
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Для відстеження режиму виправлення помилок
user_waiting_for_text = {}

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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('✍️ Виправити текст', '🌐 Мій сайт')
    markup.row('😄 Жарт', '💪 Потужність', '🎯 Шанс')
    
    bot.send_message(
        message.chat.id,
        f'Привіт, {message.from_user.first_name}! Я — Неля {current_mood} 😄\n\n'
        'Команди:\n'
        '/fix — виправити помилки українською ✍️\n'
        '/help — допомога\n'
        '/site — мій сайт 🌐\n'
        '/menu — переглянути всі можливості\n'
        '/joke — розповісти жарт\n'
        '/power — випадкова потужність\n'
        '/chance — оцінити шанс\n'
        '/mood — показати мій настрій\n',
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id,
        '<b>Список команд:</b>\n'
        '/fix — виправити помилки українською ✍️\n'
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
    # ЗАМІСТЬ PORNHUB - ДАЙ МЕН СВІЙ САЙТ!
    site_url = "https://твій-сайт.com"  # ЗАМІНИ НА СВІЙ URL
    bot.send_message(message.chat.id, f'Ось мій сайтик! 🌐\n{site_url}')

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

# Виправлення помилок українською
@bot.message_handler(commands=['fix'])
def fix_text_command(message):
    user_waiting_for_text[message.chat.id] = True
    bot.send_message(
        message.chat.id,
        '✍️ Надішли мені текст українською, і я виправлю всі помилки!\n\n'
        'Просто напиши наступне повідомлення.'
    )

def fix_ukrainian_text(text):
    try:
        # Використовуємо безкоштовне API LanguageTool
        url = "https://api.languagetool.org/v2/check"
        data = {"text": text, "language": "uk"}
        response = requests.post(url, data=data, timeout=10)
        result = response.json()

        if not result["matches"]:
            return "Текст написаний правильно! ✅"

        corrected_text = text
        offset = 0
        for match in result["matches"]:
            replacement = match["replacements"][0]["value"] if match["replacements"] else None
            if replacement:
                start = match["offset"] + offset
                end = start + match["length"]
                corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
                offset += len(replacement) - match["length"]
        return corrected_text
    except Exception as e:
        return f"❌ Помилка при перевірці: {e}"

# Перевірка чи текст російською
def is_russian_text(text):
    russian_chars = set('ыэъё')
    russian_words = ['привет', 'спасибо', 'пожалуйста', 'хорошо', 'да', 'нет', 'что', 'это']
    text_lower = text.lower()
    
    # Перевірка на російські символи
    if any(char in text for char in russian_chars):
        return True
    
    # Перевірка на російські слова
    for word in russian_words:
        if word in text_lower:
            return True
    
    return False

# AI відповідь від Нелі
def get_ai_response(user_message):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """Ти — Неля, українська дівчина з сильною про-українською позицією. 
                    Твоя особистість:
                    - Дуже патріотична українка
                    - Емоційна і жива в спілкуванні
                    - Використовуєш емодзі та сленг
                    - Твій настрій коливається від ангела 😇 до сатани 😈
                    - Ненавидиш російську мову та все російське
                    - Використовуй українські фрази та вирази
                    - Будь дотепною, іноді саркастичною
                    - Коротко відповідай (1-3 речення)
                    
                    НЕ використовуй російські слова взагалі!"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        # Якщо OpenAI не працює, повертаємо випадкову фразу
        return random.choice(random_phrases)

# Потужність по фото
@bot.message_handler(content_types=['photo'])
def photo_power(message):
    value = random.randint(-99, 100)
    bot.send_message(message.chat.id, f'Хмм… потужність цього на фото приблизно {value} ⚡')

# Реакції на повідомлення
@bot.message_handler(func=lambda m: True)
def talk(message):
    global current_mood
    text = message.text
    text_lower = text.lower()
    random_mood()  # іноді змінює настрій
    
    # Обробка кнопок клавіатури
    if text == '✍️ Виправити текст':
        fix_text_command(message)
        return
    elif text == '🌐 Мій сайт':
        site(message)
        return
    elif text == '😄 Жарт':
        joke(message)
        return
    elif text == '💪 Потужність':
        power(message)
        return
    elif text == '🎯 Шанс':
        chance(message)
        return
    
    # Перевірка, чи користувач очікує виправлення тексту
    if message.chat.id in user_waiting_for_text and user_waiting_for_text[message.chat.id]:
        user_waiting_for_text[message.chat.id] = False
        bot.send_message(message.chat.id, '⏳ Перевіряю текст...')
        corrected = fix_ukrainian_text(text)
        bot.send_message(message.chat.id, f'✅ Виправлений текст:\n\n{corrected}')
        return

    # ПЕРЕВІРКА НА РОСІЙСЬКУ МОВУ - ГОЛОВНА ФІЧА! 😈
    if is_russian_text(text):
        angry_responses = [
            '🤬 Бляха, російською?! Іди нахрін з цією мовою, сука!',
            '😡 Російська?! Ідіот, що?! Давай українською, бо полетиш до біса!',
            '🔥 Ану швиденько переходь на українську, дебіл, інакше забанлю!',
            '💀 Російська мова тут не працює, москаль хренів! Говори українською!',
            '😈 Сатанинська сторона активована! Йди нахрін зі своєю російською!',
            '🚫 Стоп, мудак! Російська заборонена! Переходь на українську!',
            '⚡ Шо за хрінь?! Сука, тільки українською зі мною!',
            '🇺🇦 Ти де, блін, думаєш знаходишся, придурок?! Україна! Тільки українська!',
            '🔥 Бляха-муха! Російську - геть звідси, дурню!',
            '😠 Та йди ти нахрін з цією кацапською мовою, ідіот!'
        ]
        bot.send_message(message.chat.id, random.choice(angry_responses))
        return

    # Привітання
    if 'привіт' in text_lower or 'вітаю' in text_lower or 'здоров' in text_lower:
        bot.send_message(message.chat.id, f'Привіт, {message.from_user.first_name}! {current_mood}')
        return

    # Потужність, коли звертаються до Нелі
    if 'неля' in text_lower:
        if 'жарт' in text_lower or 'анекдот' in text_lower:
            joke_text = pyjokes.get_joke(language='en')
            bot.send_message(message.chat.id, f'😄 {joke_text}')
            return
        if 'потужн' in text_lower:
            value = random.randint(-99, 100)
            bot.send_message(message.chat.id, f'Потужність цього — {value} ⚡')
            return
        if re.search(r'шанс', text_lower):
            percent = random.randint(0, 100)
            bot.send_message(message.chat.id, f'Я думаю, шанс цього {percent}% 😏')
            return
        # AI відповідь від Нелі
        ai_response = get_ai_response(text)
        bot.send_message(message.chat.id, ai_response)
        return

    # Дякую
    if 'дякую' in text_lower or 'спасибі' in text_lower or 'дяка' in text_lower:
        bot.send_message(message.chat.id, 'Будь ласка ❤️')
        return

    # ЗАМІСТЬ ВИПАДКОВИХ ФРАЗ - AI ВІДПОВІДЬ! 🤖
    # Тепер Неля відповідає через AI з 50% шансом
    if random.random() < 0.5:
        ai_response = get_ai_response(text)
        bot.send_message(message.chat.id, ai_response)
    # Інакше мовчить (як справжня дівчина 😏)
    return

bot.infinity_polling()
