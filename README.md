# 🤖 ChatBot Project — AI Асистент для Університету

Цей проєкт — інтелектуальний чат-бот, розроблений на базі **FastAPI**, **Ollama** та **LLM-моделей** (наприклад, Mistral, Phi), з підтримкою локального контексту, вбудованим пошуком по знаннях, стримінгом відповідей і сучасним інтерфейсом у стилі Microsoft Teams / iOS.

## 🔧 Основні функції

- 🔍 **Пошук по контексту**: бот читає файл `university_texts.txt` і шукає релевантну інформацію за допомогою FAISS та SentenceTransformer.
- 🧠 **LLM інтеграція**: Mistral, Phi, або інші моделі, що працюють через Ollama.
- 🧵 **Streaming-відповіді**: відповіді надходять у режимі реального часу.
- 🎨 **Сучасний UI**: адаптивний дизайн, темна тема, ефекти "typing", стилізовані повідомлення, авто-прокрутка.
- 🔐 **Оптимізація prompt’ів**: враховано обмеження в 2048 токенів, стискання контексту.
- ☁️ **Розгортання на Azure VM** або запуск локально.

## ⚙️ Структура проєкту

```
chatbot_project/
├── app/
│   ├── ollama_client.py      # Клас для взаємодії з Ollama та обробки контексту
│   ├── static/               # CSS / JS / assets
│   └── templates/            # HTML-шаблони (Jinja2)
├── documents/university_texts.txt  # Твій текстовий контекст
├── main.py                   # FastAPI логіка
├── .env                      # Налаштування середовища
├── Dockerfile                # FastAPI Docker
├── docker-compose.yml        # FastAPI + Ollama
├── requirements.txt          # Python залежності
```

## 🚀 Швидкий старт

1. Встанови [Docker](https://www.docker.com/products/docker-desktop)

2. Клонуй проєкт:

```bash
git clone https://github.com/pro100ham/chatbot_project.git
cd chatbot_project
```

3. Створи `.env`:

```env
MODEL_NAME=mistral
ACTIVE_ENV=local
LOCAL_OLLAMA_URL=http://host.docker.internal:11434
DOCKER_OLLAMA_URL=http://ollama:11434
```

4. Запуск:

```bash
docker-compose up --build
```

📍 Веб-інтерфейс: [http://localhost:8000](http://localhost:8000)  
📍 Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ Розгортання на Azure VM

1. Підключись:

```bash
ssh -i your_key.pem azureuser@<your-vm-ip>
```

2. Встанови Docker:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

3. Скопіюй проєкт і запусти:

```bash
scp -r -i your_key.pem ./chatbot_project azureuser@<your-vm-ip>:~
cd chatbot_project
docker-compose up --build -d
```

📍 Перевір: `http://<your-vm-ip>:8000`

---

## 🧠 Моделі Ollama

У контейнері `ollama` автоматично завантажується модель із `.env`, напр.:

```yaml
command: >
  sh -c "ollama pull mistral && ollama serve"
```

Або змінюй її:

```bash
curl http://localhost:11434/api/pull -d '{"name": "phi"}'
```

---

## ✨ UI Preview

![Chat Preview](app/static/img/chat_preview.png)

---

## 🔜 Плани

- [ ] Авторизація
- [ ] Адмін-панель
- [ ] Інтеграція з базою даних
- [ ] Підтримка PDF / CSV / API як джерела знань

---

MIT License © 2025
