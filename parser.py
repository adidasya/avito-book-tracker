import os
import requests
import time
from datetime import datetime
import urllib.parse
import concurrent.futures

# Конфигурация
TOKEN = os.getenv('TG_TOKEN', '7521422533:AAE2UaEpXpH8yh22gM2nAy3iQKg2EqAkYts')
CHAT = os.getenv('TG_CHAT', '819701342')

# СПИСОК КНИГ (ваши 65 книг) - оставить без изменений

def send_telegram(text, silent=False):
    """Отправка сообщения в Telegram"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={
            'chat_id': CHAT,
            'text': text,
            'parse_mode': 'HTML',
            'disable_notification': silent
        }, timeout=5)
        return r.status_code == 200
    except:
        return False

def check_book(book):
    """Проверка одной книги на Авито"""
    query = urllib.parse.quote(book)
    url = f"https://www.avito.ru/rossiya/knigi_i_zhurnaly?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            book_lower = book.lower()
            page_lower = response.text.lower()
            
            # Ищем ключевые слова из названия
            words = book_lower.split()[:3]
            if words and all(word in page_lower for word in words if len(word) > 2):
                return True, url, book
    except:
        pass
    
    return False, url, book

def main():
    """ОСНОВНАЯ ФУНКЦИЯ - уведомления ТОЛЬКО при находке"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Проверка {len(BOOKS)} книг")
    
    found_books = []
    start_time = time.time()
    
    # Параллельная проверка
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_book = {executor.submit(check_book, book): book for book in BOOKS}
        
        for future in concurrent.futures.as_completed(future_to_book):
            found, url, book = future.result()
            
            if found:
                found_books.append((book, url))
                # 🎯 ВОТ ЕДИНСТВЕННОЕ УВЕДОМЛЕНИЕ (при находке)
                message = (
                    f"🎯 <b>НАЙДЕНА КНИГА!</b>\n\n"
                    f"📖 <b>{book}</b>\n"
                    f"🔗 <a href='{url}'>Смотреть на Авито</a>\n"
                    f"⏰ {datetime.now().strftime('%H:%M')}"
                )
                send_telegram(message)
                print(f"✅ Найдена: {book}")
    
    # Статистика только в консоль (не в Telegram)
    elapsed = time.time() - start_time
    print(f"📊 Проверено: {len(BOOKS)} книг за {elapsed:.1f} сек")
    print(f"✅ Найдено: {len(found_books)} книг")

if __name__ == "__main__":
    main()
