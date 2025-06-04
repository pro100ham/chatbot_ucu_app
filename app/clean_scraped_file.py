import re
from langdetect import detect
from difflib import SequenceMatcher

def is_ukrainian(text):
    try:
        lang = detect(text)
        return lang == "uk"
    except:
        return False

def is_duplicate(new_block, existing_blocks, threshold=0.95):
    for block in existing_blocks:
        similarity = SequenceMatcher(None, block, new_block).ratio()
        if similarity > threshold:
            return True
    return False

def clean_scraped_ukrainian_text(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        raw = f.read()

    blocks = raw.split("\n\n")
    cleaned_blocks = []
    skipped = 0

    for block in blocks:
        block = re.sub(r"&[a-z]+;", "", block)            # HTML entities
        block = re.sub(r"\s+", " ", block).strip()         # Пробіли

        if len(block) < 50:
            skipped += 1
            continue

        if not is_ukrainian(block):
            skipped += 1
            continue

        if any(x in block.lower() for x in [
            "перейти до", "навігація", "редагувати", "категорія", "вхід", "змінити", "панель", "логін"
        ]):
            skipped += 1
            continue

        if is_duplicate(block, cleaned_blocks):
            skipped += 1
            continue

        cleaned_blocks.append(block)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(cleaned_blocks))

    print(f"✅ Очистка завершена: залишено {len(cleaned_blocks)} блоків, пропущено {skipped}.")

clean_scraped_ukrainian_text("university_texts.txt", "university_cleaned.txt")
