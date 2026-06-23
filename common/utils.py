# common/utils.py
import os
import requests
import logging

# 📝 Убедитесь, что переменные совпадают с теми, что в test_send.py
os.environ.setdefault("TELEGRAM_API_PROXY", "https://my-tg-proxy.kostya-barnung.workers.dev")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "8498316158:AAEWJwXS72nKTlQeA0gNcswZN4dx1uZmPnY")

logger = logging.getLogger(__name__)

TELEGRAM_API_PROXY = os.environ.get("TELEGRAM_API_PROXY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def send_telegram_message(chat_id: int, message: str):
    """
    Отправляет сообщение через Cloudflare Worker (прокси).
    Используется для уведомлений менеджера о заказах.
    """
    if not TELEGRAM_API_PROXY or not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_API_PROXY или TELEGRAM_BOT_TOKEN не заданы!")
        return None

    url = f"{TELEGRAM_API_PROXY}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Telegram error (url={url}): {e}")
        return None