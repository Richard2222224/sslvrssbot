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
        "name": "🖨️ Принтер",
        "file": "printers.txt"
    },
    {
        "url": "https://www.ss.com/lv/electronics/computers/monitors/rss/",
        "name": "🖥️ Монитор",
        "file": "monitors.txt"
    }
]

def load_saved_links(filename):
    """Загружает сохранённые ссылки из файла"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_links(filename, links):
    """Сохраняет ссылки в файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')

def send_telegram(text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Отправлено: {text[:50]}...")
            return True
        else:
            print(f"❌ Ошибка {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_feed(feed_info):
    """Проверяет один RSS-канал"""
    print(f"\n🔍 Проверяю: {feed_info['name']}")
    
    # Загружаем старые ссылки
    old_links = load_saved_links(feed_info['file'])
    print(f"   📁 Сохранено ранее: {len(old_links)} ссылок")
    
    # Получаем текущие объявления
    feed = feedparser.parse(feed_info['url'])
    current_links = []
    
    for entry in feed.entries[:20]:
        current_links.append(entry.link)
    
    print(f"   📥 Получено сейчас: {len(current_links)} объявлений")
    
    # Ищем новые ссылки
    new_links = []
    for link in current_links:
        if link not in old_links:
            new_links.append(link)
    
    print(f"   🆕 Новых: {len(new_links)}")
    
    # Отправляем уведомления о новых
    if len(old_links) > 0:  # Только если это НЕ первый запуск
        for link in new_links:
            message = f"🔔 Новое объявление!\n\n{feed_info['name']}\n\n🔗 {link}"
            send_telegram(message)
            time.sleep(1)  # Пауза между сообщениями
    else:
        print(f"   ℹ️ Первый запуск — уведомления не отправляются")
    
    # Сохраняем текущие ссылки
    save_links(feed_info['file'], current_links)
    print(f"   💾 Сохранено {len(current_links)} ссылок в {feed_info['file']}")
    
    return len(new_links)

def main():
    print("="*60)
    print("🤖 RSS Telegram Bot")
    print(f"⏰ Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    total_new = 0
    
    for feed_info in RSS_FEEDS:
        new_count = check_feed(feed_info)
        total_new += new_count
    
    print(f"\n{'='*60}")
    print(f"✅ Проверка завершена. Всего новых: {total_new}")
    print("="*60)

if __name__ == "__main__":
    main()
