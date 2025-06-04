# Повторний запуск після скидання середовища
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import hashlib
import json
from tqdm import tqdm

# Конфігурація
MAX_DEPTH = 5
MAX_PAGES_PER_SITE = 300
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Фільтрація посилань
def is_valid_link(link, base_domain, visited):
    return (
        urlparse(link).netloc == base_domain
        and link not in visited
        and "?do=" not in link
        and "/en:" not in link
        and not any(x in link for x in ["#top", "#nav", "/feed", ".pdf", ".docx", "mailto:"])
    )

# Черговий скрапер
def scrape_site(start_url):
    print(f"🔎 Старт: {start_url}")
    base_domain = urlparse(start_url).netloc
    visited = set()
    queue = deque([(start_url, 0)])
    text_blocks = []

    while queue and len(visited) < MAX_PAGES_PER_SITE:
        url, depth = queue.popleft()
        if depth > MAX_DEPTH or url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            main = soup.find("main") or soup.body
            title = soup.title.string.strip() if soup.title else ""
            header = main.find("h1").get_text(strip=True) if main and main.find("h1") else ""
            if main:
                text = " ".join(main.stripped_strings)
                combined = f"{title}\n{header}\n{text}"
                if len(combined) > 100:
                    text_blocks.append(combined.strip())

            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"].split("#")[0])
                if is_valid_link(link, base_domain, visited):
                    queue.append((link, depth + 1))

            if len(visited) % 10 == 0:
                print(f"🔄 {base_domain}: опрацьовано {len(visited)} сторінок...")

        except Exception as e:
            print(f"[❌] Помилка {url}: {e}")

    return base_domain, text_blocks

# Унікалізація
def remove_duplicates(blocks):
    seen = set()
    unique = []
    for block in blocks:
        h = hashlib.sha256(block.encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(block)
    return unique

# Збереження
def save_blocks(blocks, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 🛠 створює директорію, якщо треба
    with open(filename, "w", encoding="utf-8") as f:
        for block in blocks:
            f.write(block.strip() + "\n\n")
    print(f"✅ Збережено {len(blocks)} блоків у {filename}")

# Основна функція
def main(start_urls, output_path):
    all_blocks = []
    for url in tqdm(start_urls, desc="Сайти"):
        domain, blocks = scrape_site(url)
        for i, block in enumerate(blocks, 1):
            all_blocks.append(f"[Сайт: {domain}] [Розділ {i}]\n{block}")

    unique_blocks = remove_duplicates(all_blocks)
    save_blocks(unique_blocks, output_path)

# Виклик
urls = [
    "https://lvbs.com.ua/home",
    "https://wiki.ucu.edu.ua/start",
    "https://ucu.edu.ua/index",
    "https://vstup.ucu.edu.ua/start",
    "https://er.ucu.edu.ua/home"
 ]

output_file = "../../university_texts_cleaned.txt"
main(urls, output_file)
