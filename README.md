# Telegram Web App — Интерактивная новелла с выборами

Описание:
- Telegram Mini App (Web App внутри Telegram)
- Интерактивный сюжет с выбором веток, картинками и разными концовками
- Прогресс пользователя сохраняется в облачной БД (Turso)
- Бесплатный хостинг: GitHub Pages (Frontend) + Render (Backend) + Turso (DB)

Стек:
- Frontend: HTML/CSS/JS (vanilla)
- Backend: Python (FastAPI + aiogram 3.x) — API и бот в одном сервисе
- База данных: Turso (облачный SQLite), fallback на локальный SQLite
- Хостинг: GitHub Pages (Frontend) + Render (Backend, 1 сервис)

Структура проекта:
- backend/
  - __init__.py
  - db.py             (Turso / SQLite — хранение прогресса)
  - story.json        (пример истории на стороне бэкенда)
  - bot.py            (aiogram 3.x — polling для локальной разработки)
  - api.py            (FastAPI: REST API + Telegram webhook — единый сервис)
  - run_all.sh        (запуск на Render)
  - requirements.txt  (зависимости)
- frontend/
  - index.html        (веб-приложение внутри Telegram)
  - story.json        (структура сцен для фронтенда)
  - main.js           (логика веб-интерфейса)
  - styles.css        (стили)
  - assets/           (папка с картинками; добавьте свои)
- .env.example        (шаблон переменных окружения)

---

Инструкция по деплою (пошагово):

1) Создать Turso базу данных (бесплатно):
- Зарегистрируйтесь: https://turso.tech
- Установите CLI: curl -sSfL https://get.tur.so/install.sh | bash
- turso auth login
- turso db create interactive-novel
- turso db tokens create interactive-novel
- Запишите TURSO_DATABASE_URL и TURSO_AUTH_TOKEN

2) Подготовка frontend (GitHub Pages):
- Создайте репозиторий: https://github.com/your-username/interactive-novel-frontend
- Поместите содержимое frontend/ (index.html, story.json, main.js, styles.css, assets/)
- В main.js замените API_BASE на URL вашего Render-сервиса
- Включите GitHub Pages в настройках репозитория (Settings → Pages → Deploy from branch: main)

3) Подготовка backend (Render — 1 сервис):
- Создайте репозиторий с backend/ на GitHub
- На https://render.com создайте Web Service (Free tier)
- Root Directory: оставьте пустым (или укажите корень проекта)
- Build Command: pip install -r backend/requirements.txt
- Start Command: uvicorn backend.api:app --host 0.0.0.0 --port $PORT
- Установите переменные окружения (Environment Variables):
  • TELEGRAM_BOT_TOKEN — токен бота из @BotFather
  • WEBAPP_URL — URL фронтенда (https://yourname.github.io/interactive-novel-frontend/)
  • TURSO_DATABASE_URL — URL вашей Turso базы
  • TURSO_AUTH_TOKEN — токен Turso
- Webhook Telegram настроится автоматически при старте сервиса (через RENDER_EXTERNAL_URL)

4) Замените API_BASE в frontend/main.js:
- const API_BASE = 'https://your-service-name.onrender.com';

5) Путь пользователя:
- /start → кнопка → Web App → initDataUnsafe.user.id → загрузка прогресса → выбор сцен → сохранение прогресса

Локальная разработка:
- Скопируйте .env.example в .env и заполните
- pip install -r backend/requirements.txt
- Без Turso: не задавайте TURSO_DATABASE_URL — будет использован локальный SQLite
- Бот (polling): python -m backend.bot
- API: uvicorn backend.api:app --reload --port 8000

Бесплатные лимиты:
- GitHub Pages: безлимитный трафик
- Render: 750 ч/мес (1 сервис 24/7), засыпает через 15 мин неактивности
- Turso: 9 ГБ хранилища, 500M reads/мес
