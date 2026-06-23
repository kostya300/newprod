# store/management/commands/telegram_poll.py
from django.core.management.base import BaseCommand
import requests
import json
import time

class Command(BaseCommand):
    help = "Long Polling для Telegram через Cloudflare Worker"

    def handle(self, *args, **options):
        offset = 0
        token = "8498316158:AAEWJwXS72nKTlQeA0gNcswZN4dx1uZmPnY"
        PROXY = "https://my-tg-proxy.kostya-barnung.workers.dev"
        django_url = "https://myunitmyunit1.ru/api/telegram/link/"

        print(f"🚀 Long Polling запущен. Прокси: {PROXY}")

        while True:
            try:
                url = f"{PROXY}/bot{token}/getUpdates"
                params = {"offset": offset, "timeout": 10}
                response = requests.post(url, json=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data.get("ok"):
                    updates = data.get("result", [])
                    print(f"📥 Получено {len(updates)} update'ов")
                    for update in updates:
                        offset = update["update_id"] + 1
                        print("📥 Получен update:")
                        print(json.dumps(update, indent=2, ensure_ascii=False))

                        message = update.get("message")
                        if not message:
                            print("⚠️ Не найдено сообщение")
                            continue

                        text = message.get("text")
                        print(f"📌 Сообщение: '{text}'")

                        if text == '/start':
                            parts = text.split(' ')
                            print(f"🔍 parts = {parts}")
                            if len(parts) > 1 and parts[1].startswith('chat_'):
                                user_id = parts[1].replace('chat_', '')
                                telegram_chat_id = message["chat"]["id"]

                                print(f"✅ Найден user_id={user_id}, chat_id={telegram_chat_id}")

                                try:
                                    api_response = requests.post(django_url, json={
                                        "user_id": user_id,
                                        "telegram_chat_id": telegram_chat_id
                                    }, timeout=10)
                                    print(f"✅ Django API: {api_response.status_code}")
                                    print(f"   Response: {api_response.text}")
                                except Exception as e:
                                    print(f"❌ Django API error: {e}")
                            else:
                                print("⚠️ Не найден аргумент '/start chat_...'")
            except requests.exceptions.RequestException as e:
                print(f"❌ Telegram error: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ General error: {e}")
                time.sleep(5)