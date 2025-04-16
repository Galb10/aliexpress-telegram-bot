from datetime import datetime
from pytz import timezone
import requests
import random
import time
import schedule
import telegram
from bs4 import BeautifulSoup

# הגדרות
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
AFFILIATE_NAME = "Dailyalifinds"
PRODUCTS_PER_BATCH = 4

bot = telegram.Bot(token=BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TEXT_BANK = {
    "default": [
        "למה לא היה לי את זה קודם?! תראו איזה דבר",
        "תודו שזה גאוני... חייב בכל בית",
        "המצאה של החיים, כל יום שולחים לי על זה שאלה",
        "כל פעם שאני משתמש בזה שואלים אותי מאיפה קניתי",
        "אם אתם לא עם זה - אתם לא בעניינים",
    ]
}

def get_trending_products():
    url = "https://www.aliexpress.com/w/wholesale-trending.html"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a[href*='item']")

    products = []
    for item in items:
        title = item.get("title") or item.text.strip()
        link = item.get("href")
        if not link.startswith("http"):
            link = "https:" + link
        image_tag = item.find("img")
        image = image_tag.get("src") if image_tag else None
        if title and link and image:
            affiliate_link = f"{link}?aff_fcid={AFFILIATE_NAME}"
            products.append({
                "title": title,
                "link": affiliate_link,
                "image": image,
                "text": random.choice(TEXT_BANK["default"])
            })
        if len(products) >= 10:
            break
    return products

def send_products():
    print("שליחת מוצרים...")
    try:
        products = get_trending_products()
        selected = random.sample(products, PRODUCTS_PER_BATCH)
        for product in selected:
            bot.send_photo(
                chat_id=CHAT_ID,
                photo=product["image"],
                caption=f"{product['text']}\n{product['link']}"
            )
            time.sleep(3)
    except Exception as e:
        print("שגיאה בשליחה:", e)

# שליחה אוטומטית 3 פעמים ביום
schedule.every().day.at("08:30").do(send_products)
schedule.every().day.at("13:00").do(send_products)
schedule.every().day.at("20:00").do(send_products)

# ריצה מתמשכת
while True:
    schedule.run_pending()
    time.sleep(30)
