# store/utils.py
import requests
import base64
import uuid
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Кэш токена
_cached_token = None
_token_expires_at = 0  # время, когда токен перестанет быть валидным


def get_gigachat_token():
    global _cached_token, _token_expires_at

    # Если токен ещё валиден — возвращаем его
    if _cached_token and time.time() < _token_expires_at:
        return _cached_token

    # Иначе запрашиваем новый
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    client_id = "019dbe18-36f9-738d-9258-0a657a42db7f"
    client_secret = "897389bb-3b8d-4e7e-9d4a-95c0b91a88aa"

    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'Basic {creds}',
        'RqUID': str(uuid.uuid4()),
    }

    payload = {'scope': 'GIGACHAT_API_PERS'}

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            _cached_token = data.get("access_token")
            # Устанавливаем время истечения (например, на 28 минут раньше, чем надо)
            _token_expires_at = time.time() + 1680  # 28 минут в секундах
            return _cached_token
        else:
            print("❌ Ошибка получения токена:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Exception при получении токена:", str(e))
        return None