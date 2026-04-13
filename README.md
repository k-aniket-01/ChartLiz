# 📈 ChartLiz

> **A Python-first stock market learning platform** — real-time charts, candlestick pattern recognition, paper trading, and smart alerts. Built with Django. Hosted live at [chartliz-v2.onrender.com](https://chartliz-v2.onrender.com).

---

## 🌐 Live Demo

**[https://chartliz-v2.onrender.com](https://chartliz-v2.onrender.com)**

> ⚠️ Running on Render's free tier — first load may take ~30 seconds to spin up.

---

## 🧠 What is ChartLiz?

ChartLiz is a full-stack stock market education and simulation platform built entirely in Python/Django. It's designed for beginner-to-intermediate traders who want to:

- Learn candlestick patterns with real annotated charts
- Practice trading risk-free with a $100,000 paper portfolio
- Set price and pattern-based alerts
- Understand technical indicators like RSI, MACD, and Bollinger Bands

---

## ✨ Features

### 📊 Real-Time Charting
- Candlestick charts powered by TradingView's Lightweight Charts
- Multiple timeframes: 1m / 5m / 1h / 1D
- Live candle updates via WebSocket
- Volume sub-chart, multi-pane layout

### 📐 Technical Indicators
- Simple Moving Averages (SMA 20 / 50 / 200)
- RSI (14-period) with overbought/oversold lines
- MACD (line, signal, histogram)
- Bollinger Bands (upper/lower with shading)
- Toggle each indicator on/off from the UI

### 🕯️ Candlestick Pattern Recognition
- Detects: Doji, Hammer, Engulfing, Shooting Star, Morning Star, Three White Soldiers and more
- Powered by `pandas-ta` CDL functions
- Patterns annotated directly on the chart as markers
- Hover tooltip with pattern explanation and educational content
- Pattern strength score based on volume confirmation + trend context
- Full pattern history log per symbol

### 💼 Paper Trading Simulator
- Start with $100,000 virtual cash
- Market orders (instant execution at live price)
- Limit orders (Celery-monitored, triggers at target price)
- Stop-loss and take-profit automation
- Real-time portfolio dashboard with P&L per position
- P&L history chart, full trade history, CSV export
- Reset and archive sessions anytime

### 🔔 Alerts & Notifications
- Price alerts, pattern alerts, indicator-based alerts
- Real-time in-app notification bell via WebSocket
- Email notifications via Gmail SMTP
- Notification center with read/unread state

### 📚 Education Layer
- Pattern library with chart examples and signal explanations
- Indicator glossary (RSI, MACD, Bollinger explained simply)
- Beginner knowledge quiz with score tracking
- Trading journal — attach notes to each trade
- Simple strategy backtester (e.g. "buy on Hammer, sell after 3 candles")
- Leaderboard — top traders by P&L%, weekly reset

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Django 5.x |
| **Async / WebSockets** | Django Channels, ASGI |
| **Task Queue** | Celery + Celery Beat |
| **Message Broker** | Redis |
| **Database** | MySQL |
| **Market Data** | yfinance |
| **Technical Analysis** | pandas-ta |
| **Charting** | TradingView Lightweight Charts (JS) |
| **Auth** | django-allauth (email + Google OAuth) |
| **Frontend** | Bootstrap 5, vanilla JS |
| **Deployment** | Render (web service + Redis) |
| **Secrets Management** | python-decouple (.env) |

> 🐍 **Python-first philosophy:** Every business logic layer — data fetching, indicator calculation, pattern detection, order execution, alert evaluation, backtesting — is written in Python. JavaScript is used only for UI interactivity and charting.

---

## 🚀 Local Setup

### Prerequisites
- Python 3.12+
- MySQL (Community Server)
- Redis

### 1. Clone & create virtual environment

```bash
git clone https://github.com/yourusername/chartliz.git
cd chartliz

python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=chartliz
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

REDIS_URL=redis://127.0.0.1:6379/0

EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

> ⚠️ Never commit `.env` to git. It's already in `.gitignore`.

### 4. Set up the database

```bash
# In MySQL:
CREATE DATABASE chartliz;

# Then run migrations:
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start all services (3 terminals)

**Terminal 1 — Django dev server:**
```bash
python manage.py runserver
```

**Terminal 2 — Celery worker:**
```bash
celery -A chartliz worker --loglevel=info
```

**Terminal 3 — Celery Beat (scheduler):**
```bash
celery -A chartliz beat --loglevel=info
```

> Redis must also be running: `redis-server` (or `brew services start redis` on Mac)

### 6. Open in browser

```
http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
chartliz/
├── chartliz/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py         # ASGI config for Channels
│   └── celery.py       # Celery app config
│
├── users/              # Custom user model, auth, profiles
├── stocks/             # yfinance fetcher, OHLCV models, watchlist
├── trading/            # Portfolio, positions, order execution
├── alerts/             # Alert models, Celery evaluation, notifications
│
├── templates/          # Django HTML templates (Bootstrap 5)
├── static/             # CSS, JS, Lightweight Charts
│
├── requirements.txt
├── .env                # (not committed)
└── Procfile            # For Render deployment
```

---

## 🏗️ Development Phases

| Phase | Focus |
|---|---|
| 1 | Foundation — auth, user model, base UI |
| 2 | Real-time data pipeline — yfinance + WebSockets |
| 3 | Charting & technical indicators |
| 4 | Candlestick pattern recognition engine |
| 5 | Paper trading simulator |
| 6 | Alerts & notifications |
| 7 | Education, polish & extras |

---

## ☁️ Deployment (Render)

ChartLiz is deployed on [Render](https://render.com) using:

- **Web Service** — Django app via `gunicorn` + `uvicorn` (ASGI for Channels)
- **Redis** — Render Redis instance for Channels layer + Celery broker
- **MySQL** — External MySQL host (e.g. PlanetScale or Railway MySQL)

### `Procfile`

```
web: gunicorn chartliz.asgi:application -k uvicorn.workers.UvicornWorker
worker: celery -A chartliz worker --loglevel=info
beat: celery -A chartliz beat --loglevel=info
```

### Key environment variables on Render

Set these in the Render dashboard under **Environment**:

```
SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=chartliz-v2.onrender.com
DATABASE_URL=mysql://...
REDIS_URL=redis://...
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
```

---

## 🔑 Key Python Libraries

```txt
django>=5.0
django-allauth          # Auth + Google OAuth
channels                # WebSockets (ASGI)
channels-redis          # Redis channel layer
celery                  # Async task queue
redis                   # Redis client
yfinance                # Market data (OHLCV)
pandas-ta               # Technical indicators + pattern detection
mysqlclient             # MySQL Django adapter
python-decouple         # .env management
gunicorn                # Production WSGI server
uvicorn                 # ASGI worker (for Channels)
```

---

## 🤝 Contributing

ChartLiz is a learning project. If you find bugs or want to suggest improvements:

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: add X"`
4. Push and open a Pull Request

---


<div align="center">

Built with 🐍 Python · Django · ❤️ for learners

**[Live at chartliz-v2.onrender.com](https://chartliz-v2.onrender.com)**

</div>
