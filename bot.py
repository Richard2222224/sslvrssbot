import os
import time
import requests
import feedparser
from datetime import datetime

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
RSS_URL = "https://www.ss.com/lv/electronics/computers/printers-scanners-cartridges/printers/rss/"
STATE_FILE = "last_check.txt"

def get_last_check_time():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return float(f.read().strip())
    return 0

def save_last_check_time(timestamp):
    with open(STATE_FILE, 'w') as f:
        f.write(str(timestamp))

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def check_rss():
    feed = feedparser.parse(RSS_URL)
    last_check = get_last_check_time()
    current_time = time.time()
    new_items = []

    for entry in feed.entries:
        pub_time = time.mktime(entry.published_parsed)
        if pub_time > last_check:
            new_items.append(entry)

    if new_items:
        for item in reversed(new_items):
            title = item.title
            link = item.link
            description = item.get('description', 'Нет описания')
            
            message = f"🔔 <b>Новое объявление</b>\n\n"
            message += f"📌 {title}\n\n"
            message += f"{description}\n\n"
            message += f"🔗 <a href='{link}'>Открыть объявление</a>"
            
            send_telegram_message(message)
            time.sleep(1)  # пауза между сообщениями
    
    save_last_check_time(current_time)
    print(f"✅ Проверка завершена. Найдено новых: {len(new_items)}")

if __name__ == "__main__":
    check_rss()
