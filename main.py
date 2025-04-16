import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from telegram import Bot
import time
import random

# הגדרות הבוט והקבוצה
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
AFFILIATE_NAME = "Dailyalifinds"

bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler(timezone=timezone("Asia/Jerusalem"))

# ניסוח שיווקי בשרני עם אימוג'ים – 5 שורות לפחות
def generate_rich_text(title, price, link):
    emojis = ["🔥", "✅", "🛒", "💡", "✨", "📦", "❤️", "⚡", "🚀", "⭐"]
    intro = random.choice([
        "תעצור הכל – זה משהו שאתה פשוט חייב להכיר",
        "כזה דבר לא רואים כל יום – ויש סיבה לזה",
        "מצאתי לך את המוצר שכולם מדברים עליו",
        "הדבר הקטן הזה? הולך לשדרג לך את היום",
        "אם אתה אוהב דברים חכמים ושימושיים – זה בדיוק בשבילך"
    ])
    detail = random.choice([
        "מלא בסטייל, שימושי בטירוף, והכי חשוב – במחיר שבא לפנק",
        "נראה טוב, עובד מעולה, וכל מי שניסה פשוט עף",
        "הקטע הזה? כל מי שקנה – חזר לעוד אחד",
        "רמה גבוהה, מחיר נמוך – מה צריך יותר?",
        "זה פשוט עובד. בלי שטויות. בלי חרטות."
    ])
    cta = random.choice([
        "הקישור פה למטה – תלחץ ותגלה",
        "מי שמבין עניין – לא מהסס",
        "זה הולך להיגמר – תפס לפני כולם",
        "קח הצצה – תבין לבד למה כולם עפים על זה",
        "אני כבר בפנים. אתה?"
    ])

    lines = [
        f"{random.choice(emojis)} {intro}",
        f"{random.choice(emojis)} {title}",
        f"{random.choice(emojis)} {detail}",
    ]

    if price:
        lines.append(f"{random.choice(emojis)} מחיר: {price}")

    lines.append(f"{random.choice(emojis)} <a href='{link}'>לצפייה במוצר</a>")
    lines.append(f"{random.choice(emojis)} {cta}")

    return "\n".join(lines)

# שליפת מחיר מהמוצר
def get_price(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.select_one("meta[property='product:price:amount']")
        return f"{tag['content']} ₪" if tag else None
    except:
        return None

# שליפת תמונה
def get_image(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        img = soup.find("meta", property="og:image")
        return img["content"] if img else None
    except:
        return None

# יצירת קישור שותף מותאם לכל מוצר
def generate_affiliate_link(url):
    return f"https://s.click.aliexpress.com/deep_link.htm?aff_short_key=UneMJZf&dl_target_url={url}&af={AFFILIATE_NAME}"

# שליפת מוצרים טרנדיים
def get_trending_products(limit=4):
    url = "https://www.aliexpress.com/w/wholesale-trending.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href*='/item/']")
    products = []

    for link in links:
        href = link.get("href")
        if not href.startswith("http"):
            href = "https:" + href
        title = link.get("title") or link.text.strip()
        if not title:
            continue

        image = get_image(href)
        if not image:
            continue

        price = get_price(href)
        products.append({
            "title": title[:100],
            "url": href,
            "price": price,
            "image": image
        })

        if len(products) >= limit:
            break

    return products

# שליחת מוצר לקבוצה
def send_product(product):
    affiliate_link = generate_affiliate_link(product['url'])
    caption = generate_rich_text(product['title'], product['price'], affiliate_link)

    try:
        bot.send_photo(chat_id=CHAT_ID, photo=product['image'], caption=caption, parse_mode="HTML")
    except Exception as e:
        print("שגיאה בשליחה:", e)

# שליחת סדרת מוצרים
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
