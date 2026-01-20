import os
import time
import requests
import feedparser
from datetime import datetime

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# RSS-каналы
RSS_FEEDS = [
    {
        "url": "https://www.ss.com/lv/electronics/computers/printers-scanners-cartridges/printers/rss/",
        "name": "🖨️ Принтеры"
    },
    {
        "url": "https://www.ss.com/lv/electronics/computers/monitors/rss/",
        "name": "🖥️ Мониторы"
    }
]

STATE_FILE = "last_check.txt"

def get_last_items():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                return set(content.split('\n'))
    return set()

def save_last_items(items):
    with open(STATE_FILE, 'w') as f:
        f.write('\n'.join(items))

def send_telegram_message(text):
    print(f"\n📤 Попытка отправить сообщение...")
    print(f"   BOT_TOKEN: {BOT_TOKEN[:20]}... (длина: {len(BOT_TOKEN) if BOT_TOKEN else 0})")
    print(f"   CHAT_ID: {CHAT_ID}")
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не установлен!")
        return False
    
    if not CHAT_ID:
        print("❌ ОШИБКА: CHAT_ID не установлен!")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"   Статус ответа: {response.status_code}")
        
        result = response.json()
        print(f"   Ответ API: {result}")
        
        if response.status_code == 200 and result.get('ok'):
            print("✅ Сообщение успешно отправлено!")
            return True
        else:
            print(f"❌ Ошибка отправки: {result.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при отправке: {type(e).__name__}: {e}")
        return False

def check_rss():
    print(f"\n🚀 Запуск проверки RSS в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ТЕСТОВОЕ сообщение
    test_msg = "🧪 Тестовое сообщение! Бот запущен и работает!"
    if send_telegram_message(test_msg):
        print("✅ Тестовое сообщение успешно отправлено в Telegram!")
    
    last_items = get_last_items()
    # ... остальной код

    current_items = set()
    new_count = 0
    
    print(f"📊 Последних элементов в памяти: {len(last_items)}")

    for feed_info in RSS_FEEDS:
        try:
            print(f"\n🔍 Проверяю: {feed_info['name']}")
            feed = feedparser.parse(feed_info['url'])
            
            print(f"   Получено элементов: {len(feed.entries)}")
            
            for entry in feed.entries[:20]:
                item_id = entry.link
                current_items.add(item_id)
                
                if item_id not in last_items and len(last_items) > 0:
                    title = entry.title
                    link = entry.link
                    description = entry.get('description', 'Нет описания')
                    
                    print(f"\n   🆕 НОВОЕ: {title[:50]}...")
                    
                    message = f"{feed_info['name']} <b>Новое объявление</b>\n\n"
                    message += f"📌 {title}\n\n"
                    message += f"{description}\n\n"
                    message += f"🔗 <a href='{link}'>Открыть объявление</a>"
                    
                    if send_telegram_message(message):
                        new_count += 1
                    
                    time.sleep(2)
        
        except Exception as e:
            print(f"❌ Ошибка проверки {feed_info['name']}: {e}")
    
    save_last_items(current_items)
    print(f"\n✅ Проверка завершена. Найдено новых: {new_count}")
    print(f"📊 Всего элементов сейчас: {len(current_items)}")

if __name__ == "__main__":
    print("="*60)
    print("🤖 RSS Telegram Bot")
    print("="*60)
    check_rss()
    print("="*60)
