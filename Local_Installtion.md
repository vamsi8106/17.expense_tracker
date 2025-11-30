# Expense Tracker AI – MCP + FastAPI + Streamlit + PostgreSQL + Redis + Docker

A fully containerized **AI-powered Expense Assistant** built with:

* **FastAPI** (backend API)
* **Streamlit** (UI)
* **LangGraph + MCP** (agent framework)
* **PostgreSQL** (persistent DB)
* **Redis** (caching + session storage)
* **Prometheus + Grafana** (monitoring dashboard)
* **Docker** (deployment ready)

This README covers complete **local setup**, **environment configuration**, **running via Docker**, and **monitoring setup**, but **does NOT include AWS CI/CD** (kept separately in `docs/deploy.md`).

---

# 📂 Project Structure

> Note: The project now includes a `models/` folder for SQLAlchemy model definitions and no longer uses `requirements.txt` (pyproject + uv only).

```
17.expense-tracker/
│
├── src/
│   ├── agent/               → LangGraph Chat Agent
│   ├── api/                 → FastAPI backend
│   ├── config/              → Settings loader
│   ├── frontend/            → Streamlit UI
│   ├── mcp_servers/         → MCP Expense Tool Server
│   ├── utils/               → Redis, DB, logging, metrics
│
├── monitoring/
│   └── prometheus.yml       → Prometheus config
│
├── logs/                    → Mounted log directory
models/                  → SQLAlchemy models (Expense model)
.dockerignore            → Docker build exclusions
.gitignore               → Git exclusions
├── .env                     → Environment variables
├── Dockerfile               → Combined Streamlit + FastAPI container
├── requirements.txt
├── pyproject.toml
└── uv.lock
```

---

# 🚀 1. Clone the Repository

```
git clone https://github.com/vamsi8106/17.expense-tracker.git
cd 17.expense-tracker
```

---

# 🔧 2. Environment Setup

Create your `.env` file:

```
API_URL=http://localhost:8000/chat

#########################################
# DATABASE (POSTGRES)
#########################################
DATABASE_URL=postgresql+psycopg://db_user:db_pass@localhost:5432/expense_db

#########################################
# REDIS CONFIG
#########################################
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=yourpass

#########################################
# LOGGING
#########################################
LOG_FILE=/app/logs/app.log
```

---

# 🗄️ 3. PostgreSQL Setup (Local)

### Create user & DB

```
sudo -u postgres psql
```

Inside psql:

```
CREATE USER db_user WITH PASSWORD 'db_pass';
CREATE DATABASE expense_db OWNER db_user;
GRANT ALL PRIVILEGES ON DATABASE expense_db TO db_user;
```

### Verify

```
psql -U db_user -d expense_db -h localhost -W
```

---

# 🔴 4. Redis Setup (Local)

Install Redis:

```
sudo apt install redis
sudo systemctl enable redis
sudo systemctl start redis
```

Test:

```
redis-cli ping
```

---

# 🧪 5. Run Locally (Development – without Docker)

Before running the app locally for the first time, initialize PostgreSQL tables.

### Initialize DB Schema

```
python3 -c "from src.utils.init_postgres import init_db; init_db()"
```

This creates the `expenses` table using SQLAlchemy models defined under:

```
src/models/expense.py
```

### Start Backend (Development – without Docker)

### Terminal 1 → backend

```
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 → Streamlit frontend

```
streamlit run src/frontend/app.py
```

Open UI:
👉 [http://localhost:8501](http://localhost:8501)

---

# 🐳 6. Docker Build & Run & Run

### Build Image

```
docker build -t expense_app:latest .
```

### Run Container

```
docker run -d \
  --name expense_app_container \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -p 8000:8000 \
  -p 8501:8501 \
  expense_app:latest
```

Open:

* FastAPI → [http://localhost:8000](http://localhost:8000)
* Streamlit → [http://localhost:8501](http://localhost:8501)
* Metrics → [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

# 📊 7. Monitoring with Prometheus + Grafana

Your monitoring setup includes Prometheus + Grafana **AND** a custom dashboard JSON:

* `monitoring/prometheus.yml` → Prometheus configuration
* `monitoring/grafana-dashboard-expense-monitoring.json` → Importable Grafana dashboard

### Start Prometheus

```
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Start Grafana

```
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

### Import the dashboard

1. Open Grafana → [http://localhost:3000](http://localhost:3000)
2. Go to **Dashboards → Import**
3. Upload file: `monitoring/grafana-dashboard-expense-monitoring.json`
4. Select Prometheus datasource
5. Dashboard loads instantly

---

# 🧠 8. How the Agent Works How the Agent Works

ASCII architecture:

```
User → Streamlit → FastAPI → Chat Agent
        │              │
        │              ├── Redis (sessions + cache)
        │              ├── MCP Server (expense tools)
        │              └── PostgreSQL (persistent DB)
```

MCP tools include:

* add_expense
* list_expenses
* expenses_between
* category_summary

---

# 📡 9. MCP Server Architecture

```
FastAPI → LangGraph → MCP Client → Expense Tracker Server
                                           │
                                           └── PostgreSQL
```

The MCP server runs internally via stdio inside the container.

---

# 📁 10. Log Storage

Logs are stored in the host directory:

```
logs/app.log
```

Mounted to container via:

```
-v $(pwd)/logs:/app/logs
```

---

# 🧪 11. Example Prometheus Metrics

* `llm_api_calls_total`
* `mcp_tool_calls_total`
* `cache_hits_total`
* `cache_misses_total`
* `active_users_total`
* `expenses_added_total`
* `llm_api_latency_seconds`

---

# 🛠️ 12. Troubleshooting

### MCPError: Connection closed

→ Ensure Python path is correct in Docker.
→ MCP server included in same container; no extra ports needed.

### PostgreSQL “connection refused”

Check:

```
sudo ss -lntp | grep 5432
```

If DB runs on EC2 → use public IP.

### Redis “NOAUTH” error

Provide password in `.env`:

```
REDIS_PASSWORD=abc123
```

### Logs not writing

Ensure logs directory exists:

```
mkdir -p logs
chmod 777 logs
```

---

# 🎉 13. You're Ready to Use the Expense Assistant!

Start container and open:

* UI → [http://localhost:8501](http://localhost:8501)
* API → [http://localhost:8000](http://localhost:8000)
* Metrics → [http://localhost:8000/metrics](http://localhost:8000/metrics)
* Prometheus → [http://localhost:9090](http://localhost:9090)
* Grafana → [http://localhost:3000](http://localhost:3000)

For AWS deployment steps → see `docs/deploy.md`.

---

# 🙌 Credits

Built by **Vamsi** with LangGraph, MCP, Streamlit, FastAPI & PostgreSQL.
