import requests

token = "7375577655:AAE9NBUIn3pNrxkPChS5V2nWA0Fs6bnkeNA"
chat_id = "-1002644464460"

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": text
}

response = requests.post(url, data=payload)
print(response.text)
