# test_send.py (в корне проекта, рядом с manage.py)
import requests
import json

# 🔑 УБЕДИТЕСЬ: эти значения правильные!
PROXY = "https://my-tg-proxy.kostya-barnung.workers.dev"  # ← ваш URL из Cloudflare
TOKEN = "8498316158:AAEWJwXS72nKTlQeA0gNcswZN4dx1uZmPnY"
CHAT_ID = 1006498329  # ваш ID из getUpdates

# ✅ ВАЖНО: без /bot{token} — он добавляется в worker.js!
url = f"{PROXY}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "✅ Тестовое сообщение от VikiMarketBot! Бот через Worker работает ✅",
    "parse_mode": "HTML",
}

print("🚀 Отправка запроса на:", url)
print("   chat_id:", CHAT_ID)

try:
    response = requests.post(url, json=payload, timeout=10)
    print("✅ Статус:", response.status_code)

    result = response.json()
    print("📋 Ответ:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("ok"):
        print("\n📌 УСПЕХ! Сообщение отправлено. Проверьте Telegram.")
    else:
        print(f"\n❌ Ошибка Telegram: {result.get('description')}")
except Exception as e:
    print(f"❌ Ошибка запроса: {e}")