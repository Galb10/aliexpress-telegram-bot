import requests
import random
import time
import schedule
import os

# משתנים מהסביבה
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "-1002644464460"

# ניסוחים שיווקיים לפי קטגוריה
TEMPLATES = {
    "default": [
        "למה לא היה לי את זה קודם?!",
        "מי שמוותר על זה – שיאכל את הלב",
        "שיא האלגנט, במחיר בדיחה",
        "מוצר קטן, חיים קלים",
        "לא יאומן כמה זה שימושי"
    ],
    "kitchen": [
        "העוזר הקטן שלא ידעת שאתה צריך",
        "במטבח שלי – זה כבר כוכב",
        "כפפות? לא צריך – יש את זה",
        "הסוד של כל שף ביתי"
    ],
    "tech": [
        "גאונות פשוטה = חובה בסל",
        "איך לא חשבו על זה קודם?!",
        "כל חובב טכנולוגיה צריך את זה",
        "אין מצב שאתה נשאר בלי זה"
    ]
}

# שליחת הודעה עם תמונה ובקישור
def send_telegram_message(text, photo_url):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "caption": text, "photo": photo_url}
    )

# יצירת טקסט שיווקי
def generate_caption(title, price, url, category="default"):
    template = random.choice(TEMPLATES.get(category, TEMPLATES["default"]))
    return f"{template}\n\n{title}\n\nרק ב־{price}₪\n{url}"

# מוצרים לדוגמה (תשולב כאן API אמיתי בהמשך)
def get_trending_products():
    return [
        {
            "title": "קולפן ירקות 3 ב-1 נירוסטה",
            "price": "9.90",
            "image": "https://ae01.alicdn.com/kf/image.jpg",
            "url": "https://s.click.aliexpress.com/e/_kitchen1",
            "category": "kitchen"
        },
        {
            "title": "מעמד טלפון מסתובב לרכב",
            "price": "15.40",
            "image": "https://ae01.alicdn.com/kf/image2.jpg",
            "url": "https://s.click.aliexpress.com/e/_tech2",
            "category": "tech"
        },
        {
            "title": "מספריים למטבח מולטי",
            "price": "12.80",
            "image": "https://ae01.alicdn.com/kf/image3.jpg",
            "url": "https://s.click.aliexpress.com/e/_kitchen2",
            "category": "kitchen"
        }
    ]

# שליחה של כמה מוצרים (3–5)
def send_products():
    products = get_trending_products()
    chosen = random.sample(products, min(5, len(products)))
    for product in chosen:
        caption = generate_caption(
            product["title"], product["price"], product["url"], product.get("category", "default")
        )
        send_telegram_message(caption, product["image"])
        time.sleep(2)

# תזמון יומי – 3 פעמים ביום
schedule.every().day.at("09:00").do(send_products)
schedule.every().day.at("13:00").do(send_products)
schedule.every().day.at("18:00").do(send_products)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
