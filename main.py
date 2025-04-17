import requests
import time
import random
import os
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

# פרטי טלגרם ו-Admitad שלך
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
ADMITAD_PREFIX = "https://rzekl.com/g/1e8d11449475164bd74316525dc3e8/?ulp="

sent_file = "sent_products.txt"
headers = {"User-Agent": "Mozilla/5.0"}

def load_sent():
    if not os.path.exists(sent_file):
        return set()
    with open(sent_file, "r") as f:
        return set(f.read().splitlines())

def save_sent(url):
    with open(sent_file, "a") as f:
        f.write(url + "\n")

def generate_message(product):
    title = product['title']
    url = product['url']
    image = product['image']
    link = ADMITAD_PREFIX + requests.utils.quote(url)

    if any(x in title.lower() for x in ["shirt", "חולצה", "t-shirt", "טישרט"]):
        return f"""<b>👕 חולצה בסטייל שלא תישאר הרבה במלאי!</b>

{title}

היא מושלמת לקיץ – קלילה, נוחה ומלאת נוכחות. אם אתה בקטע של לבלוט – זאת שלך.

<a href="{link}">לצפייה במוצר</a>"""
    elif any(x in title.lower() for x in ["light", "lamp", "מנורה", "led", "לד"]):
        return f"""<b>💡 תאורה שתשנה את האווירה בבית!</b>

{title}

עיצוב נקי, מראה מודרני, ואור שנותן תחושה יוקרתית.

<a href="{link}">לפרטים נוספים</a>"""
    elif any(x in title.lower() for x in ["bag", "תיק", "backpack"]):
        return f"""<b>🎒 תיק פרקטי ויפה – השילוב המנצח!</b>

{title}

גם נוח, גם איכותי, וגם נראה מיליון דולר. מושלם ליום-יום.

<a href="{link}">למוצר המלא</a>"""
    elif any(x in title.lower() for x in ["usb", "גאדג'", "מטען", "כבל", "charger"]):
        return f"""<b>🔌 גאדג'ט שיפתור לך בעיה יומיומית!</b>

{title}

מינימלי, חכם, ועם פתרון שמקל עליך ביום יום.

<a href="{link}">בדוק את המוצר</a>"""
    else:
        return f"""<b>✨ מציאה מפתיעה מאלי אקספרס!</b>

{title}

תוספת מושלמת לבית או ליומיום – במחיר שלא תמצא בארץ.

<a href="{link}">הצצה למוצר</a>"""

def fetch_products():
    url = "https://bestsellers.aliexpress.com"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select(".item")[:20]
    products = []
    for item in items:
        a = item.find("a", href=True)
        img = item.find("img", src=True)
        if not a or not img:
            continue
        link = a["href"]
        if not link.startswith("http"):
            continue
        title = img.get("alt", "מוצר מעלי אקספרס")
        image = img["src"]
        products.append({"title": title.strip(), "url": link.strip(), "image": image.strip()})
    return products

def send(product):
    msg = generate_message(product)
    payload = {
        "chat_id": CHAT_ID,
        "photo": product["image"],
        "caption": msg,
        "parse_mode": "HTML"
    }
    response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)
    if response.status_code == 200:
        save_sent(product["url"])
    else:
        print("שגיאה בשליחה:", response.text)

def send_batch():
    print("שולח מוצרים...")
    sent = load_sent()
    products = fetch_products()
    random.shuffle(products)
    count = 0
    for p in products:
        if p["url"] not in sent and p["image"]:
            send(p)
            count += 1
            time.sleep(5)
        if count >= 4:
            break

# תזמון והרצה ראשונית
scheduler = BlockingScheduler(timezone=timezone("Asia/Jerusalem"))
scheduler.add_job(send_batch, "cron", hour="9,14,20")
send_batch()
scheduler.start()

def send_batch():
    print("התחלנו את הפונקציה send_batch")
    sent = load_sent()
    products = fetch_products()
    print(f"נמצאו {len(products)} מוצרים")

    random.shuffle(products)
    count = 0
    for p in products:
        if p["url"] not in sent and p["image"]:
            print("שולח מוצר:", p["title"])
            send(p)
            count += 1
            time.sleep(5)
        if count >= 4:
            break
