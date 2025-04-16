import requests
import pytz
from bs4 import BeautifulSoup
import telegram
from telegram.error import TelegramError
from apscheduler.schedulers.background import BackgroundScheduler
import random
import time

BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
PARTNER_NAME = "Dailyalifinds"

bot = telegram.Bot(token=BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ניסוחים לדוגמה
CAPTIONS = [
    "למה אף אחד לא אמר לי על זה קודם?!", "איפה זה היה כל החיים שלי", "דבר כזה פשוט אי אפשר להשאיר בעגלה",
    "תשאירו מקום בבית, זה נכנס", "מי שיש לו את זה – יודע", "לא תאמינו מה המחיר", "תראו איזה גאונות",
    "תודו שזה מטורף", "כזה אתם עוד לא ראיתם", "שדרוג מושלם לבית", "תשאירו מקום במדף", "אני כבר הזמנתי",
]

def get_trending_products(limit=5):
    url = "https://www.aliexpress.com/"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for item in soup.select("a[href*='/item/']")[:limit * 2]:  # לוקחים כפול כדי לסנן מוצרים בעייתיים
        href = item.get("href")
        img_tag = item.select_one("img")
        title = img_tag.get("alt") if img_tag else None
        image_url = img_tag.get("src") or img_tag.get("image-src") if img_tag else None

        if href and title and image_url and image_url.startswith("http"):
            affiliate_link = f"{href}?aff_fcid=2f2d98f71a7f40bfbbcd3cb8fc6e91c3-1702218993732-07763-_eT1FRX&aff_fsk=_eT1FRX&aff_platform=portals-tool&sk=_eT1FRX&aff_trace_key=2f2d98f71a7f40bfbbcd3cb8fc6e91c3-1702218993732-07763-_eT1FRX&terminal_id=ae3056e3b25b4e29a149df8c90b246f0&af=2264024&cv=47843&afref=&mall_affr=pr3&utm_source=admitad&utm_medium=cpa&utm_campaign={PARTNER_NAME}"
            products.append({
                "title": title.strip(),
                "image_url": image_url.strip(),
                "url": affiliate_link
            })
        if len(products) >= limit:
            break
    return products

def send_products():
    try:
        products = get_trending_products()
        print("שולח מוצרים...")

        for product in products:
            caption = f"{random.choice(CAPTIONS)}\n\n{product['title']}\n{product['url']}"
            try:
                bot.send_photo(chat_id=CHAT_ID, photo=product["image_url"], caption=caption)
                time.sleep(5)
            except TelegramError as e:
                print(f"שגיאה בשליחת מוצר: {e}")
                bot.send_message(chat_id=CHAT_ID, text=caption)
    except Exception as e:
        print(f"שגיאה כללית: {e}")

# הגדרה של תזמון
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Jerusalem"))
scheduler.add_job(send_products, 'cron', hour=9, minute=0)   # בוקר
scheduler.add_job(send_products, 'cron', hour=14, minute=0)  # צהריים
scheduler.add_job(send_products, 'cron', hour=20, minute=0)  # ערב
scheduler.start()

# הרצה ראשונית לבדיקה
send_products()

# שמירה שהקוד יישאר חי
while True:
    time.sleep(60)
