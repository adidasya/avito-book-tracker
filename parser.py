import os
import requests
import time
from datetime import datetime, timedelta
import urllib.parse
import re

# КОНФИГУРАЦИЯ
TOKEN = os.getenv('TG_TOKEN', '7521422533:AAE2UaEpXpH8yh22gM2nAy3iQKg2EqAkYts')
CHAT = os.getenv('TG_CHAT', '819701342')

BOOKS = [
    "Путь одного агентства",
    "Доказательная медицина талантов",
    "0,05 доказательная медицина",
    "Ritz Carlton",
    "Благоволительницы",
    "Синдром Паганини",
    "Мастерство учителя",
    "Масштаб",
    "Человек на все рынки",
    "Стратегии гениев",
    "Дневник реалиста",
    "Первые 20 часов",
    "Принцип Абрамовича",
    "Укрощение амигдалы",
    "Пятая дисциплина",
    "Сложные решения",
    "Как люди учатся",
    "наказание наградой",
    "инноваторы",
    "Парадокс перфекциониста",
    "Мотивация для творческих людей",
    "как рождаются эмоции",
    "взлом креатива",
    "карточки рисовый штурм",
    "В поисках памяти",
    "Расстроенная психика",
    "кислород",
    "код Петцольд",
    "почему я отвлекаюсь",
    "принцип ставок",
    "сначала заплати себе",
    "элегия хиллбилли",
    "спин продажи",
    "Неприятие перемен",
    "Эффективный руководитель",
    "Время Березовского",
    "Биохакинг",
    "Память не изменяет",
    "Инвестиции",
    "О Шрифте",
    "мастер историй",
    "рома едет",
    "тишина",
    "бесстрашие",
    "в постели с врагом",
    "главная книга основателя бизнеса",
    "глазами физика",
    "год без покупок",
    "ешь правильно беги быстро",
    "как это построено",
    "искусство сторителлинга",
    "мастер слова",
    "Шпион на миллиард долларов",
    "код дурова",
    "люди среди деревьев",
    "меняю жир на силу воли",
    "мясо с кровью",
    "на одной волне",
    "огилви о рекламе",
    "моя жизнь в рекламе",
    "ошибки на миллион долларов",
    "парадокс перфекциониста",
    "слон на танцполе",
    "сотрудники на всю жизнь",
    "ультрамышление",
    "первые 90 дней",
    "18 минут",
    "Со мной хотят общаться",
    "Радость изнутри"
]

def send_telegram(text):
    """Универсальная отправка в Telegram"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={
            'chat_id': CHAT,
            'text': text,
            'parse_mode': 'HTML'
        }, timeout=5)
        return r.status_code == 200
    except:
        return False

def extract_time_from_text(time_text):
    """
    Преобразует текст времени от Авито в объект datetime
    Примеры: "сегодня 10:30", "вчера 14:20", "25 февраля 15:40"
    """
    now = datetime.now()
    
    # Приводим к нижнему регистру
    time_text = time_text.lower().strip()
    
    # 1. СЕГОДНЯ
    if time_text.startswith('сегодня'):
        time_str = time_text.replace('сегодня', '').strip()
        try:
            hour, minute = map(int, time_str.split(':'))
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 2. ВЧЕРА
    elif time_text.startswith('вчера'):
        time_str = time_text.replace('вчера', '').strip()
        try:
            hour, minute = map(int, time_str.split(':'))
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except:
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 3. ДАТА (например, "25 февраля 15:40")
    else:
        try:
            # Парсим русскую дату
            day_str, month_str, time_str = time_text.split()
            day = int(day_str)
            
            # Русские месяцы
            months = {
                'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
            }
            
            month = months.get(month_str, now.month)
            
            # Время
            hour, minute = map(int, time_str.split(':'))
            
            # Год (если месяц больше текущего, значит прошлый год)
            year = now.year
            if month > now.month:
                year = now.year - 1
            
            return datetime(year, month, day, hour, minute)
        except:
            return None

def is_within_last_24_hours(publish_time):
    """Проверяет, было ли объявление за последние 24 часа"""
    if not publish_time:
        return False
    
    now = datetime.now()
    time_diff = now - publish_time
    
    # Проверяем, что разница менее 24 часов
    return time_diff.total_seconds() <= 24 * 3600

def search_avito(book):
    """
    Поиск объявлений на Авито с точной проверкой времени
    """
    query = urllib.parse.quote(book)
    
    # Используем сортировку по дате (самые новые)
    url = f"https://www.avito.ru/rossiya/knigi_i_zhurnaly?cd=1&q={query}&s=104"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.avito.ru/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Проверка на блокировку
        if response.status_code != 200:
            return None, None, None, False
        
        page = response.text
        
        # Ищем ВСЕ объявления на странице
        # Паттерн для поиска блоков объявлений
        item_pattern = r'<div[^>]*data-marker="item"[^>]*>.*?</div>\s*</div>\s*</div>'
        items = re.findall(item_pattern, page, re.DOTALL)
        
        if not items:
            return None, None, None, False
        
        for item_html in items[:5]:  # Проверяем первые 5 объявлений
            # Ищем ссылку
            link_match = re.search(r'href="(/[^"]+/\d+)"', item_html)
            if not link_match:
                continue
            
            item_url = f"https://www.avito.ru{link_match.group(1)}"
            
            # Ищем дату публикации
            date_match = re.search(r'data-marker="item-date"[^>]*>([^<]+)<', item_html)
            if not date_match:
                continue
            
            publish_text = date_match.group(1).strip()
            
            # Ищем цену
            price_match = re.search(r'data-marker="item-price"[^>]*>([^<]+)<', item_html)
            price = price_match.group(1).strip() if price_match else "цена не указана"
            
            # Ищем заголовок
            title_match = re.search(r'itemprop="name"[^>]*content="([^"]+)"', item_html)
            title = title_match.group(1) if title_match else book
            
            # Преобразуем текст времени в datetime
            publish_time = extract_time_from_text(publish_text)
            
            # Проверяем, что объявление за последние 24 часа
            if publish_time and is_within_last_24_hours(publish_time):
                return item_url, publish_text, price, True
        
        return None, None, None, False
        
    except Exception as e:
        print(f"Ошибка поиска {book}: {e}")
        return None, None, None, False

def main():
    """Основная функция парсера"""
    current_datetime = datetime.now()
    date_str = current_datetime.strftime('%d.%m.%Y')
    time_str = current_datetime.strftime('%H:%M:%S')
    
    print(f"\n{'='*70}")
    print(f"📚 ПАРСЕР АВИТО | {date_str} {time_str}")
    print(f"📖 Книг: {len(BOOKS)} | Проверка: каждые 5 минут")
    print(f"⏰ Фильтр: только за последние 24 часа")
    print(f"{'='*70}")
    
    found_count = 0
    found_books = []
    
    # Проверка всех книг
    for i, book in enumerate(BOOKS, 1):
        print(f"[{i:2d}/{len(BOOKS)}] {book[:45]:<45}", end="")
        
        url, publish_text, price, found = search_avito(book)
        
        if found:
            found_count += 1
            found_books.append({
                'book': book,
                'url': url,
                'time': publish_text,
                'price': price
            })
            
            print(f" ✅ {publish_text} ({price})")
            
            # Форматируем сообщение для Telegram
            message = (
                f"🆕 <b>НОВОЕ ОБЪЯВЛЕНИЕ (24ч)</b>\n\n"
                f"📖 <b>{book}</b>\n"
                f"💰 {price}\n"
                f"🕒 {publish_text}\n"
                f"🔗 <a href='{url}'>Смотреть на Авито</a>\n"
                f"📅 Найдено: {time_str}"
            )
            
            # Отправляем уведомление
            send_telegram(message)
            
            # Пауза между уведомлениями
            time.sleep(0.5)
        else:
            print(f" 📭 нет новых")
        
        # Пауза между запросами к Авито
        time.sleep(1)
    
    # Итоговая статистика
    print(f"{'='*70}")
    print(f"📊 ИТОГ: {found_count} новых объявлений за 24 часа")
    
    if found_count > 0:
        print("\n📋 Найденные книги:")
        for item in found_books:
            print(f"  • {item['book']} ({item['time']})")
    
    print(f"{'='*70}")
    
    # Итоговое уведомление
    if found_count > 0:
        summary = (
            f"📊 <b>ОТЧЁТ {date_str} {time_str}</b>\n"
            f"✅ Найдено за 24 часа: {found_count} книг\n"
            f"📚 Всего проверено: {len(BOOKS)}\n"
            f"🔄 Следующая проверка через 5 минут"
        )
        send_telegram(summary)

if __name__ == "__main__":
    main()
