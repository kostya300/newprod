# debug_file.py
with open('store/fixtures/category.json', 'rb') as f:
    raw = f.read(16)
    print("Hex:", raw.hex())
    print("Bytes:", raw)