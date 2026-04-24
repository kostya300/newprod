# fix_encoding.py
import json
import os


def repair_mojibake(text):
    """Пытается восстановить текст, повреждённый из-за чтения UTF-16 как cp1251"""
    try:
        # Шаг 1: Преобразуем "битый" текст в байты как если бы он был в cp1251
        bad_bytes = text.encode('cp1251')
        # Шаг 2: Декодируем как UTF-16 Little Endian
        fixed = bad_bytes.decode('utf-16le')
        return fixed
    except Exception:
        return text  # Если не получилось — оставляем как есть


def deep_repair(data):
    """Рекурсивно исправляет строки в JSON"""
    if isinstance(data, dict):
        return {key: deep_repair(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [deep_repair(item) for item in data]
    elif isinstance(data, str):
        # Проверяем, содержит ли строка "подозрительные" символы из cp1251 → utf-16 ошибки
        if any(c in data for c in '¤ЄюЁрЁкЄхё·╣╗║╧ырэ°хЄ├┴'):
            return repair_mojibake(data)
        return data
    else:
        return data


# Путь к файлу
file_path = 'store/fixtures/product.json'

if not os.path.exists(file_path):
    print(f"❌ Файл не найден: {file_path}")
else:
    try:
        # Читаем как байты, чтобы определить реальную кодировку
        with open(file_path, 'rb') as f:
            raw = f.read()

        # Определяем кодировку
        if raw.startswith(b'\xff\xfe'):
            content = raw.decode('utf-16le')
        elif raw.startswith(b'\xef\xbb\xbf'):
            content = raw.decode('utf-8-sig')
        else:
            content = raw.decode('utf-8')

        # Парсим JSON
        data = json.loads(content)

        # Исправляем все строки
        fixed_data = deep_repair(data)

        # Сохраняем в чистом UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=4, ensure_ascii=False)

        print("✅ Файл успешно восстановлен и сохранён в UTF-8")
    except Exception as e:
        print(f"❌ Ошибка: {e}")