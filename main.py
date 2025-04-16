import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from telegram import Bot
import time
import random

# הגדרות
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
AFFILIATE_NAME = "Dailyalifinds"

bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler(timezone=timezone("Asia/Jerusalem"))

# טקסטים שיווקיים לפי קטגוריה
CATEGORY_MESSAGES = {
    "kitchen": [
        "שדרוג אמיתי למטבח במחיר של חטיף",
        "אי אפשר לבשל בלי זה – שווה כל שקל",
        "אם אתם במטבח – אתם צריכים את זה עכשיו"
    ],
    "tech": [
        "גאדג'ט מהחלומות – יגרום לך להרגיש בעתיד",
        "שדרוג חכם ומשתלם בטירוף",
        "מי שמבין עניין – לא מוותר על זה"
    ],
    "storage": [
        "כל בית צריך את זה – סדר מושלם בכמה שקלים",
        "הסוד של בתים מסודרים? הנה הוא",
        "קטן, פשוט, גאוני – אחסון כמו שצריך"
    ],
    "default": [
        "למה לא גיליתי את זה קודם?!",
        "שדרוג יומיומי שעושה הבדל גדול",
        "כל פעם שאני רואה את זה – בא לי להזמין שוב",
        "מציאה מטורפת – חובה לבדוק"
    ]
}

CATEGORY_KEYWORDS = {
    "kitchen": ["knife", "cut", "cook", "food", "pan", "kitchen", "spice"],
    "tech": ["usb", "bluetooth", "gadget", "smart", "wireless", "phone", "camera"],
    "storage": ["organizer", "storage", "box", "fold", "rack", "hanger", "vacuum"]
}

def detect_category(title):
    title = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in title for kw in keywords):
            return category
    return "default"

def get_price_from_product(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        price = soup.select_one("meta[property='product:price:amount']")
        return f"{price['content']} ₪" if price else None
    except:
        return None

def get_image_from_product(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        image = soup.find("meta", property="og:image")
        return image["content"] if image else None
    except:
        return None

def generate_affiliate_link(url):
    return f"https://s.click.aliexpress.com/deep_link.htm?aff_short_key=UneMJZf&dl_target_url={url}&af={AFFILIATE_NAME}"

def get_trending_products(limit=4):
    url = "https://www.aliexpress.com/w/wholesale-trending.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    products = []

    for a in soup.select("a[href*='/item/']"):
        href = a.get("href")
        if not href.startswith("http"):
            href = "https:" + href
        title = a.get("title") or a.text.strip()
        if not title or not href:
            continue
        price = get_price_from_product(href)
        image = get_image_from_product(href)
        if not image:
            continue
        category = detect_category(title)
        products.append({
            "title": title[:100],
            "url": href,
            "price": price or "לא הצלחנו לזהות מחיר",
            "image": image,
            "category": category
        })
        if len(products) >= limit:
            break
    return products

def send_product(product):
    message = random.choice(CATEGORY_MESSAGES.get(product["category"], CATEGORY_MESSAGES["default"]))
    caption = (
        f"{message}\n\n"
        f"<b>{product['title']}</b>\n"
        f"מחיר: {product['price']}\n"
        f"<a href='{generate_affiliate_link(product['url'])}'>לצפייה במוצר</a>"
    )
    try:
        bot.send_photo(chat_id=CHAT_ID, photo=product["image"], caption=caption, parse_mode="HTML")
    except Exception as e:
        print("שגיאה בשליחה:", e)

def send_products():
    print("שולח מוצרים...")
    products = get_trending_products()
    for product in products:
        send_product(product)
        time.sleep(3)

# תזמון אוטומטי
scheduler.add_job(send_products, 'cron', hour=9, minute=0)
scheduler.add_job(send_products, 'cron', hour=14, minute=0)
scheduler.add_job(send_products, 'cron', hour=20, minute=0)
scheduler.start()

# שליחה מיידית לבדיקה
send_products()

# שמירה על ריצה
while True:
    time.sleep(60)
