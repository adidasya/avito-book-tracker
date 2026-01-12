import requests
import os
from datetime import datetime
import time

# Получаем данные из переменных окружения GitHub
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7521422533:AAE2UaEpXpH8yh22gM2nAy3iQKg2EqAkYts')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '819701342')

BOOKS_TO_TRACK = [
    "Путь одного агентства Торбосов",
    "Доказательная медицина талантов",
    "0,05 доказательная медицина Петр Талантов",
    # ... (весь ваш список книг - я сократил для примера)
    "Радость изнутри тан"
]

def send_telegram(text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"✓ Отправлено: {text[:50]}...")
    except Exception as e:
        print(f"✗ Ошибка отправки: {e}")

def check_book(book):
    """Проверяет одну книгу на Авито"""
    query = requests.utils.quote(book)
    url = f"https://www.avito.ru/rossiya/knigi_i_zhurnaly?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if book.lower() in response.text.lower():
            return {
                'found': True,
                'book': book,
                'url': url,
                'time': datetime.now().strftime("%H:%M")
            }
    except:
        pass
    
    return {'found': False, 'book': book}

def main():
    print(f"🚀 Запуск проверки Авито")
    print(f"📚 Книг для проверки: {len(BOOKS_TO_TRACK)}")
    print(f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}")
    
    # Отправляем стартовое сообщение
    send_telegram(
        f"🔍 <b>Парсер Авито запущен на GitHub!</b>\n"
        f"📚 Книг для отслеживания: <b>{len(BOOKS_TO_TRACK)}</b>\n"
        f"⏰ Проверка каждый час\n"
        f"🕐 {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    found_count = 0
    
    # Проверяем каждую книгу
    for i, book in enumerate(BOOKS_TO_TRACK, 1):
        print(f"[{i}/{len(BOOKS_TO_TRACK)}] Проверка: {book}")
        result = check_book(book)
        
        if result['found']:
            found_count += 1
            message = (
                f"🎯 <b>НАЙДЕНА КНИГА!</b>\n\n"
                f"📖 <b>{result['book']}</b>\n"
                f"🔗 <a href='{result['url']}'>Смотреть на Авито</a>\n"
                f"⏰ {result['time']}"
            )
            send_telegram(message)
            time.sleep(1)  # Пауза между отправками
        
        time.sleep(2)  # Пауза между запросами
    
    # Отправляем итог
    summary = (
        f"📊 <b>Проверка завершена</b>\n\n"
        f"✅ Найдено книг: <b>{found_count}</b>\n"
        f"📚 Всего проверено: {len(BOOKS_TO_TRACK)}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M')}\n"
        f"🔁 Следующая проверка через 1 час"
    )
    send_telegram(summary)
    
    print(f"✅ Проверка завершена. Найдено: {found_count} книг")

if __name__ == "__main__":
    main()
