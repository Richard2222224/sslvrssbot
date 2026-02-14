import feedparser
import requests
import os
import json

RSS_FEEDS = [
    "https://www.ss.lv/lv/electronics/computers/printers-scanners-cartridges/rss/",
    "https://www.ss.lv/lv/electronics/computers/monitors/rss/"
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

STATE_FILE = "sent_items.json"

def load_sent_items():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_items(items):
    with open(STATE_FILE, "w") as f:
        json.dump(list(items), f)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def main():
    sent_items = load_sent_items()
    updated = False

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            link = entry.link
            if link not in sent_items:
                # Отправляем новое объявление
                message = f"🆕 Новое объявление:\n{entry.title}\n{link}"
                send_telegram(message)

                sent_items.add(link)
                updated = True

    if updated:
        save_sent_items(sent_items)

if __name__ == "__main__":
    main()
