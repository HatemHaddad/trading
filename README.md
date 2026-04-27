# Trading Portfolio Bot

Automated portfolio tracker for TQQQ, AGG, IBIT, and ADCB (ADC) holdings. Runs on a cron schedule, fetches live prices, calculates performance metrics, saves results to a local SQLite database, sends a Telegram report, and displays everything on a web dashboard.

## How It Works

1. `run_and_save.py` fetches 1-year price history via `yfinance`, computes portfolio metrics (including daily change, Sharpe ratio, max drawdown), saves a row to `trading.db`, and sends a Telegram report
2. `api/main.py` (FastAPI) serves the database over a REST API on port 8000
3. `web/` (React + Vite + Tailwind) reads the API and renders the live dashboard on port 3000
4. Everything is orchestrated by Docker — auto-restarts on crash or server reboot

## Project Structure

```
trading/
├── api/
│   └── main.py               # FastAPI backend
├── web/
│   └── src/                  # React + Vite dashboard
├── docker/
│   ├── nginx.conf            # nginx config for the web container
│   └── runner-crontab        # Cron schedule for the runner container
├── Dockerfile.api            # API container
├── Dockerfile.web            # Web container (Node builder → nginx)
├── Dockerfile.runner         # Cron runner container
├── docker-compose.yml        # Orchestrates all three services
├── requirements.txt          # Python dependencies
├── run_and_save.py           # Core analysis and reporting script
├── db.py                     # SQLite init and insert helpers
├── portfolio.json            # Your holdings (shares + buy prices)
├── trading.db                # SQLite database (not committed)
├── .env                      # Credentials — not committed (see .env.example)
└── .env.example              # Credentials template
```

---

## Deployment with Docker (recommended)

Docker runs all three services automatically and restarts them on crash or server reboot. No manual process management needed.

### Prerequisites

- A Linux server (Ubuntu 22.04 recommended)
- Docker and Docker Compose installed

#### Install Docker on Ubuntu

```bash
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify:
```bash
docker --version
docker compose version
```

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/HatemHaddad/trading.git
cd trading
```

### Step 2 — Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
export TELEGRAM_TOKEN=your_telegram_bot_token
export TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### Step 3 — Configure your portfolio

Edit `portfolio.json` with your actual holdings:

```json
{
  "shares_tqqq": 100,
  "buy_price_tqqq": 40.00,
  "shares_agg": 50,
  "buy_price_agg": 99.64,
  "shares_ibit": 188.63,
  "buy_price_ibit": 52.24,
  "shares_adc": 22500,
  "buy_price_adc": 5.865,
  "quarter_baseline_price_tqqq": 47.07
}
```

### Step 4 — Set the API URL for the frontend

Edit `web/.env.production` and set your server's public IP:

```bash
VITE_API_URL=http://YOUR_SERVER_IP:8000
```

### Step 5 — Build and start everything

```bash
docker compose up -d --build
```

This builds all three images and starts them in the background. The first build takes ~3–5 minutes (downloads base images and installs dependencies). Subsequent builds are much faster due to layer caching.

### Step 6 — Verify everything is running

```bash
docker compose ps
```

Expected output:
```
NAME               IMAGE            STATUS
trading-api-1      trading-api      Up
trading-runner-1   trading-runner   Up
trading-web-1      trading-web      Up
```

Test the API:
```bash
curl http://localhost:8000/api/latest
```

Open the dashboard in your browser:
```
http://YOUR_SERVER_IP:3000
```

---

## Docker — Day-to-Day Commands

| Command | What it does |
|---------|-------------|
| `docker compose up -d` | Start all services in background |
| `docker compose down` | Stop all services |
| `docker compose ps` | Show running containers and status |
| `docker compose logs -f api` | Watch API logs live |
| `docker compose logs -f runner` | Watch cron job output live |
| `docker compose logs -f web` | Watch nginx logs live |
| `docker compose up -d --build` | Rebuild images after code changes and restart |
| `docker compose restart api` | Restart just the API |

---

## Docker — How It Works Internally

### Three containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `trading-api-1` | `trading-api` | 8000 | FastAPI — serves the SQLite database as a REST API |
| `trading-web-1` | `trading-web` | 3000 | nginx — serves the compiled React dashboard |
| `trading-runner-1` | `trading-runner` | — | cron — runs `run_and_save.py` on schedule |

### Shared data (volumes)

`trading.db` and `portfolio.json` live on the host and are mounted into both `api` and `runner` containers. This means:
- Data persists if containers are rebuilt or restarted
- You can edit `portfolio.json` on the host and the runner picks it up on the next run without rebuilding

### Auto-restart

All three containers have `restart: always`. If uvicorn crashes, if nginx dies, or if the whole server reboots — Docker brings everything back automatically with no manual intervention.

### Cron in Docker

The runner container installs the system cron daemon. The cron schedule mirrors the original `crontab.txt`:

| Time | Days | Action |
|------|------|--------|
| 5:30 PM | Mon–Fri | Runs after US market close |
| 12:00 AM | Tue–Sat | Overnight run |

Cron output is routed to Docker's stdout so you can see every run with:
```bash
docker compose logs runner
```

### Environment variables

Credentials from `.env` are injected into the containers at runtime via `env_file`. They are never baked into the image — the image is safe to rebuild or share. The runner also exports them into `/etc/environment` so the cron daemon can access them (cron doesn't inherit shell environment by default).

### Web build (two-stage)

`Dockerfile.web` uses a two-stage build:
1. **Builder stage** — Node 20 installs npm dependencies and runs `vite build`
2. **Runtime stage** — copies only the compiled `dist/` into `nginx:alpine`

The final image has no Node.js, no source code, no `node_modules` — just static files and nginx (~26 MB compressed).

---

## Where Docker images are stored

Images are stored locally on your server at `/var/lib/docker/`. They are **not** pushed to Docker Hub. If you move to a new server, just clone the repo and run `docker compose up -d --build` again — it will rebuild from the Dockerfiles.

Approximate image sizes:
| Image | Size |
|-------|------|
| `trading-api` | ~118 MB |
| `trading-runner` | ~124 MB |
| `trading-web` | ~26 MB |

---

## Updating after code changes

```bash
git pull
docker compose up -d --build
```

That's it. Docker rebuilds only the layers that changed (fast due to caching) and restarts the affected containers.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/latest` | Most recent portfolio snapshot |
| `GET /api/history?limit=90` | Time-series data for the chart |
| `GET /api/runs?limit=50&offset=0` | Paginated full run history |
| `GET /api/watchlist` | SPMO momentum ETF stats |

---

## Dashboard Features

- Total portfolio value with daily $ and % change
- Per-holding cards: TQQQ, AGG, IBIT, ADC (AED-denominated with USD equivalent)
- Metrics strip: Daily Change, Daily %, Sharpe Ratio, Max Drawdown, Ann. Return
- Portfolio value chart (90-day history)
- Quarterly TQQQ rebalancing target with BUY/SELL/HOLD signal
- SPMO watchlist with momentum stats
- Full run history table with color-coded daily change column

---

## Database

Results are stored in `trading.db` (SQLite), table `runs`. Key columns:

| Column | Description |
|--------|-------------|
| `run_at` | Timestamp of the run |
| `total_curr_val` | Total portfolio value (USD) |
| `total_return` | Overall return since purchase |
| `daily_change` | Day-over-day value change (USD) |
| `daily_change_pct` | Day-over-day change (%) |
| `price_tqqq` / `price_agg` / `price_ibit` | Live closing prices |
| `price_adc` / `aed_usd_rate` | ADCB price (AED) and exchange rate |
| `sharpe` | Annualised Sharpe ratio |
| `max_drawdown` | Maximum drawdown over 1 year |
| `quarter_action` | BUY / SELL / HOLD recommendation |
| `shares_to_trade` | TQQQ shares to act on |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_TOKEN` | Telegram bot API token |
| `TELEGRAM_CHAT_ID` | Telegram chat or user ID |
| `VITE_API_URL` | API base URL for the frontend (set in `web/.env.production`) |
| `DB_PATH` | Override SQLite path (optional, defaults to `trading.db` next to `db.py`) |
