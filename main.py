import requests
import random
import time
from bs4 import BeautifulSoup
import schedule

# פרטי הבוט והקבוצה
BOT_TOKEN = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
CHAT_ID = "-1002644464460"
TRACKING_ID = "Dailyalifinds"

# טקסטים שיווקיים לפי קטגוריה
TEMPLATES = {
    "default": [
        "למה לא היה לי את זה קודם?",
        "מוצר חובה בכל בית!",
        "יאללה לעגלה!",
        "תודו לי אחר כך",
        "בקטע מוגזם – שווה כל שקל",
        "חובה אצל כל אחד!"
    ],
    "kitchen": [
        "הסוד של כל שף ביתי",
        "העוזר הקטן שאתה צריך במטבח",
        "בלי זה – אל תיכנס למטבח"
    ],
    "tech": [
        "גאדג'ט חכם במחיר מגוחך",
        "למה לשלם כפול בארץ?",
        "כל חובב טכנולוגיה חייב את זה"
    ]
}

# שליחת מוצר לטלגרם
def send_product(title, image_url, price, product_url, category="default"):
    caption = f"{random.choice(TEMPLATES.get(category, TEMPLATES['default']))}\n\n{title}\nרק ב־{price}₪\n{product_url}"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "caption": caption, "photo": image_url}
    )

# שליפת מוצרים מאלי אקספרס (דילים חמים)
def get_trending_products():
    url = "https://www.aliexpress.com/gcp/flashdeals/featured"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    for item in soup.select("a.flash-sale-item-card"):
        try:
            title = item.select_one(".title--wrap--Ms9Zv").text.strip()
            image = item.find("img")["src"]
            price = item.select_one(".uniform-banner-box-price").text.replace("US $", "").strip()
            link = "https:" + item["href"]
            affiliate_link = f"https://s.click.aliexpress.com/deep_link.htm?aff_short_key=UneMJZf&dl_target_url={link}&aff_fcid={TRACKING_ID}"
            items.append({
                "title": title,
                "image": image,
                "price": price,
                "link": affiliate_link,
                "category": "default"
            })
        except:
            continue
    return items

# שליחת 3 מוצרים אקראיים
def send_trending():
    try:
        products = get_trending_products()
        selected = random.sample(products, min(3, len(products)))
        for product in selected:
            send_product(product["title"], product["image"], product["price"], product["link"], product["category"])
            time.sleep(2)
    except Exception as e:
        print("שגיאה בשליחה:", e)

# הגדרת זמני שליחה
schedule.every().day.at("09:00").do(send_trending)
schedule.every().day.at("13:00").do(send_trending)
schedule.every().day.at("18:00").do(send_trending)

# ריצה מתמשכת
if __name__ == "__main__":
    print("הבוט פעיל וישלח מוצרים כל יום 3 פעמים...")
    while True:
        schedule.run_pending()
        time.sleep(30)
