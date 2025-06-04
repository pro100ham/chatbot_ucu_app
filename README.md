# 🤖 ChatBot Project — AI Асистент для Університету

Цей проєкт — розумний чат-бот для університету, побудований на основі **FastAPI**, **Ollama**, **OpenAI**, з підтримкою RAG-підходу, веб-пошуку, стримінгу відповідей та ведення історії сесій.

---

## 🚀 Основні можливості

- 🧠 **LLM-підтримка**: 
  - `🧠 Ollama` — локальні моделі (Mistral, Phi тощо)
  - `💬 ChatGPT` — OpenAI з локальним контекстом (RAG)
  - `🌐 ChatGPT with Web` — OpenAI з живим пошуком по сайтах
- 🔎 **RAG-пошук по контексту**: FAISS + Sentence Transformers
- 🌍 **Веб-пошук (Google Custom Search)** для зовнішніх запитів
- 🧵 **Streaming-відповіді**: live-стрім тексту
- 🕒 **Сесії користувача**: автоматичне ведення однієї активної сесії на кожну модель
- 💬 **CRM інтеграція**: створення тікетів при запитах
- 🎨 **Сучасний UI**: стиль Microsoft Teams / iOS, темна тема

---

## 🗂 Структура проєкту

```
chatbot_project/
├── app/
│   ├── LLM/                     # LLM-клієнти: Ollama, ChatGPT, ChatGPTWeb
│   ├── sessionDB/               # SQLAlchemy моделі та сесійна логіка
│   ├── utils/                   # RAG, prompt builder, streaming, web search
│   ├── templates/               # HTML шаблони
│   ├── static/                  # CSS, JS, іконки
├── documents/                   # Файли для RAG
├── .env.example                 # Приклад налаштувань
├── requirements.txt             # Python залежності
├── Dockerfile                   # Docker інструкція
├── docker-compose.yml           # FastAPI + Ollama
├── main.py                      # Основна FastAPI логіка
```

---

## ⚙️ Встановлення

### 🧰 1. Клонування та налаштування

```bash
git clone https://github.com/pro100ham/chatbot_project.git
cd chatbot_project
cp .env.example .env
```

🔒 Вкажи свій OpenAI ключ у `.env`.

---

### 🐋 2. Запуск через Docker

```bash
docker-compose up --build
```

📍 Веб-інтерфейс: [http://localhost:8000](http://localhost:8000)  
📍 Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### ☁️ 3. Розгортання на Azure VM

```bash
# Підключення
ssh -i your_key.pem azureuser@<your-vm-ip>

# Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Проєкт
scp -r -i your_key.pem ./chatbot_project azureuser@<your-vm-ip>:~
cd chatbot_project
docker-compose up --build -d
```

---

## 🧠 .env приклад

```dotenv
# LLM
MODEL_NAME=mistral
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-3.5-turbo

# URLs
LOCAL_OLLAMA_URL=http://host.docker.internal:11434
DOCKER_OLLAMA_URL=http://ollama:11434

# Google Search API (опційно для ChatGPT with Web)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
```

---

## 🧪 UI Можливості

- 🔄 Перемикання LLM: Ollama, ChatGPT, ChatGPT+Web
- 🟢 Стрімінг відповідей
- ✨ Відображення форм для тікетів
- 📱 Мобільна адаптація

---

## 🔐 Безпека

- `.env` додано до `.gitignore`
- Використання `.env.example` замість справжніх ключів
- Секрети не зберігаються в історії Git

---

## 🔮 Майбутнє

- [ ] Авторизація користувачів
- [ ] Розширений адмін-інтерфейс
- [ ] Підтримка PDF/CSV/API в якості джерел RAG
- [ ] Автоматичне завершення сесій по неактивності

---

MIT License © 2025