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

    text = ""
    if any(x in title.lower() for x in ["shirt", "חולצה", "t-shirt", "טישרט"]):
        text = f"""👕 *חולצה בסטייל שלא תישאר הרבה במלאי!*

{title}

היא מושלמת לקיץ – קלילה, נוחה ומלאת נוכחות. אם אתה בקטע של לבלוט, זאת שלך.

[צפה במוצר]({link})"""
    elif any(x in title.lower() for x in ["light", "lamp", "מנורה", "led", "לד"]):
        text = f"""💡 *תאורה שתשנה את האווירה בבית!*

{title}

פשוט, אלגנטי, ועושה חשק לעצב מחדש. תתכונן למחמאות.

[לפרטים נוספים]({link})"""
    elif any(x in title.lower() for x in ["bag", "תיק", "backpack"]):
        text = f"""🎒 *תיק פרקטי ויפה – השילוב המנצח!*

{title}

גם נוח, גם איכותי, וגם נראה מיליון דולר. מתאים לכל יציאה.

[לצפייה במוצר]({link})"""
    elif any(x in title.lower() for x in ["usb", "גאדג'", "מטען", "כבל"]):
        text = f"""🔌 *גאדג'ט שיפתור לך בעיה יומיומית!*

{title}

מינימלי, חכם, בדיוק מה שאתה לא ידעת שאתה צריך.

[למוצר המלא]({link})"""
    else:
        text = f"""✨ *מציאה ששווה בדיקה!*

{title}

לא בטוח איך חיית בלעדיה עד עכשיו. עכשיו זה הזמן לנסות.

[בדוק את המוצר]({link})"""
    return text

def fetch_products():
    url = "https://bestsellers.aliexpress.com"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select(".item")[:15]
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
        "parse_mode": "Markdown"
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)
    save_sent(product["url"])

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

scheduler = BlockingScheduler(timezone=timezone("Asia/Jerusalem"))
scheduler.add_job(send_batch, "cron", hour="9,14,20")
send_batch()
scheduler.start()
