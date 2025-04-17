import requests
import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from telegram import Bot

# פרטי הבוט והקבוצה
TELEGRAM_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
bot = Bot(token=TELEGRAM_TOKEN)

sent_products = set()

EMOJIS = ["🔥", "✨", "⚡", "🛒", "✅", "🧠", "💥"]
OPENERS = [
    "למה לא היה לי את זה קודם", "איפה זה היה כל החיים שלי", "מוצר שאי אפשר לעמוד בפניו",
    "תראו איזה טירוף", "לא תאמינו שקיים דבר כזה", "מושלם!", "זה פשוט מבריק"
]

def fetch_trending_products():
    url = "https://bestsellers.aliexpress.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    products = []
    for item in soup.select(".item")[:10]:
        link = item.find("a")["href"]
        title = item.select_one(".title").get_text(strip=True)
        image = item.find("img")["src"]
        if link not in sent_products and image and title:
            products.append({
                "title": title,
                "url": link,
                "image": image
            })
    return products

def generate_affiliate_link(original_url):
    encoded = requests.utils.quote(original_url, safe='')
    return f"https://rzekl.com/g/1e8d11449475164bd74316525dc3e8/?ulp={encoded}"

def create_marketing_message(product):
    opener = random.choice(OPENERS)
    emoji = random.choice(EMOJIS)
    title = product["title"]
    return f"""{emoji} *{opener}* {emoji}

{title}

[צפו במוצר עכשיו]({generate_affiliate_link(product["url"])})"""

def send_product_to_telegram(product):
    try:
        message = create_marketing_message(product)
        bot.send_photo(
            chat_id=CHAT_ID,
            photo=product["image"],
            caption=message,
            parse_mode="Markdown"
        )
        sent_products.add(product["url"])
        print("נשלח:", product["title"])
    except Exception as e:
        print("שגיאה:", e)

def daily_task():
    print("שולח מוצרים...")
    products = fetch_trending_products()
    selected = random.sample(products, min(4, len(products)))
    for product in selected:
        send_product_to_telegram(product)

scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")
scheduler.add_job(daily_task, "cron", hour=9)
scheduler.add_job(daily_task, "cron", hour=14)
scheduler.add_job(daily_task, "cron", hour=20)
scheduler.start()

while True:
    time.sleep(60)
