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

STATE_FILE = "last_items.json"

def load_last_items():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_items(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def main():
    last_items = load_last_items()
    updated = False

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            continue

        latest = feed.entries[0]
        link = latest.link

        if last_items.get(feed_url) != link:
            message = f"🆕 Новое объявление:\n{latest.title}\n{link}"
            send_telegram(message)

            last_items[feed_url] = link
            updated = True

    if updated:
        save_last_items(last_items)

if __name__ == "__main__":
    main()
