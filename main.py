import requests
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# פרטי הבוט והקבוצה
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
PARTNER_NAME = "Dailyalifinds"

# טקסטים שיווקיים
TEMPLATES = [
    "איך לא הכרתי את זה קודם?",
    "הולך לשנות לך את החיים!",
    "למה אף אחד לא סיפר לי על זה עד היום?",
    "לא תבינו איך הסתדרתם בלעדיו",
    "מצאתי לכם את הדבר הבא!",
    "מי שלא קונה את זה - מפסיד",
    "טירוף במחיר מצחיק!",
    "הכי שווה שראיתי לאחרונה",
    "חובה בכל בית",
    "זה פשוט גאוני",
    "המוצר הזה? בול בשבילך",
    "אין דברים כאלה",
    "סוף סוף מצאתי פתרון",
    "את זה כולם חייבים",
    "הדבר הזה משדרג כל יום",
]

# שליפת מוצרים טרנדיים
def get_trending_products(limit=4):
    url = "https://www.aliexpress.com/w/wholesale-trending.html"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("a", href=True)
    filtered = []
    for link in products:
        href = link["href"]
        if "item" in href and "html" in href:
            filtered.append("https:" + href.split("?")[0])
    return random.sample(list(set(filtered)), min(limit, len(filtered)))

# המרת קישור לקישור שותף
def generate_affiliate_link(product_url):
    return f"{product_url}?aff_fcid=123456&aff_fsk=partner&aff_platform=portals-tool&sk=partner&aff_trace_key=&terminal_id=&af=1&dp=Dailyalifinds"

# שליחת הודעה לטלגרם
def send_to_telegram(text, image_url=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "caption" if image_url else "text": text
    }
    if image_url:
        payload["photo"] = image_url
    requests.post(url, data=payload)

# שליחת מוצר
def send_product(product_url):
    affiliate_link = generate_affiliate_link(product_url)
    title = random.choice(TEMPLATES)
    image_url = get_image_from_product(product_url)
    text = f"{title}\n{affiliate_link}"
    send_to_telegram(text, image_url)

# נסיון לשלוף תמונה מהמוצר
def get_image_from_product(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        meta = soup.find("meta", property="og:image")
        return meta["content"] if meta else None
    except:
        return None

# שליחת כמה מוצרים כל פעם
def send_products():
    print("שולח מוצרים...")
    products = get_trending_products(4)
    for product in products:
        send_product(product)
        time.sleep(3)

# הרצת משימות בזמנים קבועים
scheduler = BackgroundScheduler(timezone=timezone("Asia/Jerusalem"))
scheduler.add_job(send_products, trigger='cron', hour=9, minute=0)
scheduler.add_job(send_products, trigger='cron', hour=14, minute=0)
scheduler.add_job(send_products, trigger='cron', hour=20, minute=0)
scheduler.start()
send_products()

# הרצה אינסופית
while True:
    time.sleep(60)
