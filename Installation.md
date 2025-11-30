# EC2 Installation Guide (Redis + PostgreSQL)

## 🔥 Redis Installation on EC2

### 1. SSH into EC2

```bash
ssh -i key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 2. Install Redis

```bash
sudo apt update
sudo apt install redis-server -y
```

### 3. Enable Remote Access

Edit Redis config:

```bash
sudo nano /etc/redis/redis.conf
```

Find:

```
bind 127.0.0.1 ::1
```

Change to:

```
bind 0.0.0.0
```

Set:

```
protected-mode yes
```

Enable password:
Find this in redis.conf:

```
# requirepass foobared
```

Uncomment & change:

```
requirepass YOUR_STRONG_PASSWORD
```

Example:

```
requirepass abc123
```

### 4. Restart Redis

```bash
sudo systemctl restart redis-server
sudo systemctl status redis-server
```

### 5. Configure Security Group

In AWS Console → **EC2 → Security Groups**, edit inbound rules for the Redis instance:

| Type       | Protocol | Port | Source                           |
| ---------- | -------- | ---- | -------------------------------- |
| Custom TCP | TCP      | 6379 | SG-ID of your other EC2 instance |

⚠️ **DO NOT expose Redis to 0.0.0.0/0**

### 6. Test Redis Connection

```bash
redis-cli -h YOUR_PUBLIC_IP -p 6379 -a YOUR_PASSWORD
```

Example:

```bash
redis-cli -h 34.230.77.137 -p 6379 -a abc123
```

---

## 🐘 PostgreSQL Installation on EC2

### 1. Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl status postgresql
```

### 2. Switch to postgres User

```bash
sudo -i -u postgres
psql
```

### 3. Create DB & User

Inside `psql`:

```sql
CREATE USER db_user WITH PASSWORD 'db_pass';
CREATE DATABASE mydb OWNER db_user;
GRANT ALL PRIVILEGES ON DATABASE mydb TO db_user;
```

Exit:

```bash
\q
exit
```

### 4. Allow External Connections

Edit PostgreSQL config:

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Find:

```
#listen_addresses = 'localhost'
```

Change to:

```
listen_addresses = '*'
```

Edit pg_hba.conf:

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add for same VPC access:

```
host    all     all     172.31.0.0/16     md5
```

Allow access from anywhere (ONLY if required):

```
host    all     all     0.0.0.0/0     md5
```

### 5. Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

### 6. Test PostgreSQL Connection

```bash
psql -h YOUR_PUBLIC_IP -U db_user -d mydb
```

Example:

```bash
psql -h 34.230.77.137 -U db_user -d mydb
```

# 📈 Prometheus + Grafana Installation on EC2

## 🔥 Install Prometheus

### 1. SSH into EC2

```bash
ssh -i key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 2. Create Prometheus User & Directories

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
```

### 3. Download Prometheus

```bash
cd /tmp
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-amd64.tar.gz
tar xvf prometheus-2.53.0.linux-amd64.tar.gz
cd prometheus-2.53.0.linux-amd64
```

### 4. Move Files

```bash
sudo mv prometheus /usr/local/bin/
sudo mv promtool /usr/local/bin/

sudo mv consoles /etc/prometheus
sudo mv console_libraries /etc/prometheus
sudo mv prometheus.yml /etc/prometheus
```

### 5. Set Permissions

```bash
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
```

### 6. Create Prometheus Service

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Paste:

```
[Unit]
Description=Prometheus Monitoring
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

### 7. Start Prometheus

```bash
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus
sudo systemctl status prometheus
```

### 8. Security Group Rules

| Type       | Port | Source                |
| ---------- | ---- | --------------------- |
| Custom TCP | 9090 | your IP or trusted SG |

Access Prometheus:

```
http://<EC2_PUBLIC_IP>:9090
```

---

## 📊 Install Grafana

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana -y
```

### 1. Start Grafana

```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
sudo systemctl status grafana-server
```

### 2. Access Grafana

```
http://<EC2_PUBLIC_IP>:3000
```

Default login:

```
user: admin
pass: admin
```

### 3. Add Firewall Rules

| Type       | Port | Source                |
| ---------- | ---- | --------------------- |
| Custom TCP | 3000 | your IP or trusted SG |

---

## 🔥 Add Prometheus as a Data Source in Grafana

1. Open Grafana → **Connections**
2. Go to **Data Sources** → **Add Prometheus**
3. Set URL:

```
http://<EC2_PUBLIC_IP>:9090
```

4. Click **Save & Test**

# 🖥️ Install Node Exporter on EC2 (Application Server)

## 1. SSH into Application EC2

```bash
ssh -i key.pem ubuntu@<EC2_PUBLIC_IP>
```

## 2. Download Node Exporter

```bash
cd /tmp
curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
tar xvf node_exporter-1.8.2.linux-amd64.tar.gz
sudo mv node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/
```

## 3. Create User for Node Exporter

```bash
sudo useradd --no-create-home --shell /bin/false node_exporter
```

## 4. Create node_exporter.service

```bash
sudo nano /etc/systemd/system/node_exporter.service
```

Paste:

```
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

## 5. Start Node Exporter

```bash
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

## 6. Test Node Exporter

```bash
curl http://<EC2_PRIVATE_IP>:9100/metrics
```

## 7. Security Group Rule (Application Server)

| Type       | Port | Source                             |
| ---------- | ---- | ---------------------------------- |
| Custom TCP | 9100 | Prometheus EC2 security group (SG) |

---

# 🔧 Add Node Exporter to Prometheus (prometheus.yml)

Edit file:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add these scrape jobs at the **end**:

```yaml
  - job_name: "expense_fastapi"
    metrics_path: "/metrics"
    scheme: http
    static_configs:
      - targets: ["app-server-ip:8000"]
        labels:
          service: "expense-assistant"

  # -------------------------------
  # Node Exporter (system metrics)
  # -------------------------------
  - job_name: "node_exporter"
    static_configs:
      - targets: ["app-server-ip:9100"]
        labels:
          service: "node"
```

Restart Prometheus:

```bash
sudo systemctl restart prometheus
```

# Grafana Dashboards Setup (Node Exporter + Custom Observability)

This document contains instructions for:

* Importing the **Node Exporter Full** dashboard (ID: 1860)
* Importing your **custom Expense Assistant Observability Dashboard**
* Handling the **Prometheus datasource UID** properly

---

# 📌 1. Default Node Exporter Dashboard (Port 9100)

Node Exporter exposes system metrics on port **9100**.
Grafana runs on port **3000**.
Prometheus scrapes on port **9090**.

### ✔ Import Built‑in Node Exporter Dashboard

Grafana → **Dashboards** → **Import** → enter:

```
1860
```

This imports **Node Exporter Full**, which shows:

* CPU usage
* Memory usage
* Disk I/O
* Network stats
* File system
* Load average
* System uptime

---

# 📌 2. Get Prometheus Datasource UID

Grafana assigns a unique `uid` to each datasource.
Retrieve it using:

```
http://<grafana-ip>:3000/api/datasources
```

Example output:

```json
[
  {
    "id": 1,
    "uid": "cf5n70p366kn4d",
    "name": "Prometheus",
    "type": "prometheus"
  }
]
```

Use **your actual UID** inside the dashboard JSON.

---

# 📌 3. Custom Grafana Dashboard JSON (Expense Assistant Observability)

This dashboard visualizes:

* Total LLM API calls
* RPS of LLM calls
* MCP tool invocations
* Cache hits/misses
* Latency P50/P90/P99 via histogram quantile

> ⚠️ Replace `cf5n70p366kn4d` with **your datasource UID**.

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "graphTooltip": 2,
  "liveNow": false,
  "panels": [
    {
      "datasource": { "type": "prometheus", "uid": "cf5n70p366kn4d" },
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
      "id": 1,
      "targets": [ { "expr": "sum(llm_api_calls_total)", "legendFormat": "Total LLM API Calls" } ],
      "title": "LLM API Calls (Total)",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "cf5n70p366kn4d" },
      "gridPos": { "h": 4, "w": 6, "x": 6, "y": 0 },
      "id": 2,
      "targets": [ { "expr": "sum(rate(llm_api_calls_total[5m]))", "legendFormat": "LLM RPS" } ],
      "title": "LLM Request Rate (RPS)",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "cf5n70p366kn4d" },
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 4 },
      "id": 3,
      "targets": [ { "expr": "sum(mcp_tool_calls_total)", "legendFormat": "Tool Calls" } ],
      "title": "MCP Tool Calls (Total)",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "cf5n70p366kn4d" },
      "gridPos": { "h": 4, "w": 6, "x": 6, "y": 4 },
      "id": 4,
      "targets": [
        { "expr": "sum(cache_hits_total)", "legendFormat": "Cache Hits" },
        { "expr": "sum(cache_misses_total)", "legendFormat": "Cache Misses" }
      ],
      "title": "Cache Hits vs Misses",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "cf5n70p366kn4d" },
      "gridPos": { "h": 6, "w": 12, "x": 0, "y": 8 },
      "id": 5,
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum(rate(llm_api_latency_seconds_bucket[5m])) by (le))",
          "legendFormat": "P50"
        },
        {
          "expr": "histogram_quantile(0.90, sum(rate(llm_api_latency_seconds_bucket[5m])) by (le))",
          "legendFormat": "P90"
        },
        {
          "expr": "histogram_quantile(0.99, sum(rate(llm_api_latency_seconds_bucket[5m])) by (le))",
          "legendFormat": "P99"
        }
      ],
      "title": "LLM Latency (P50 / P90 / P99)",
      "type": "timeseries"
    }
  ],
  "refresh": "10s",
  "schemaVersion": 36,
  "style": "dark",
  "title": "Expense Assistant Observability",
  "uid": "expense-obsv-v2",
  "version": 3
}
```

---

# 📌 How to Import This Custom Dashboard

Grafana → **Dashboards** → **Import** → paste the JSON above.

✔ Replace the UID before importing.
✔ Click **Load** → Select your Prometheus datasource → **Import**.

Your dashboard is now ready!

