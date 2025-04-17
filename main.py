import requests
import time
import random
import os
from datetime import datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMITAD_LINK_PREFIX = os.getenv("ADMITAD_LINK_PREFIX", "https://rzekl.com/g/1e8d11449475164bd74316525dc3e8/?ulp=")

sent_products_file = "sent_products.txt"

def fetch_trending_products():
    url = "https://best.aliexpress.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("a[href*='item']")[:10]
    products = []

    for item in items:
        link = item.get("href")
        title = item.get("title") or item.text.strip()
        if not link or not title:
            continue
        full_link = link if link.startswith("http") else f"https:{link}"
        image = item.find("img")
        img_url = image["src"] if image and "src" in image.attrs else None
        products.append({
            "title": title,
            "url": full_link,
            "img": img_url
        })

    return products

def make_affiliate_link(original_url):
    return ADMITAD_LINK_PREFIX + requests.utils.quote(original_url, safe="")

def generate_message(product, price="לא זמין"):
    message = f"""**{product['title']}**
    
הנה משהו שבאמת תצטער שלא היה לך קודם!
המוצר הזה פשוט חובה - בדיוק מסוג הדברים שאתה לא מבין איך הסתדרת בלעדיהם.
מתאים בול לסגנון שלך, גם פרקטי וגם נראה פגז.

מחיר: {price}
[למוצר המלא]({make_affiliate_link(product['url'])})
"""
    return message

def load_sent_products():
    if not os.path.exists(sent_products_file):
        return set()
    with open(sent_products_file, "r") as file:
        return set(file.read().splitlines())

def save_sent_product(url):
    with open(sent_products_file, "a") as file:
        file.write(url + "\n")

def send_product_to_telegram(product):
    if product["url"] in load_sent_products():
        return False

    affiliate_url = make_affiliate_link(product["url"])
    price = "לא זמין"
    message = generate_message(product, price)

    data = {
        "chat_id": CHAT_ID,
        "caption": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    if product.get("img"):
        data["photo"] = product["img"]
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=data)
    else:
        data["text"] = message
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)

    save_sent_product(product["url"])
    return True

def send_batch():
    print("שולח מוצרים...")
    products = fetch_trending_products()
    random.shuffle(products)
    count = 0
    for product in products:
        if send_product_to_telegram(product):
            count += 1
        if count >= 5:
            break

scheduler = BlockingScheduler(timezone=timezone("Asia/Jerusalem"))
scheduler.add_job(send_batch, "cron", hour="9,14,20")
send_batch()
scheduler.start()
