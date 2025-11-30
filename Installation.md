# EC2 Installation & Deployment Guide (Two‑Server Architecture)

This guide explains production deployment using **two EC2 servers**:

* **Monitor Node:** PostgreSQL, Redis, Prometheus, Grafana
* **Application Node:** Expense App (Docker), Node Exporter

---

# 🔥 Redis Installation (Monitor Node)

## 1. Install & Configure Redis

```bash
sudo apt update
sudo apt install redis-server -y
```

Enable remote access:

```bash
sudo nano /etc/redis/redis.conf
```

Modify:

```
bind 0.0.0.0
protected-mode yes
requirepass YOUR_PASSWORD
```
Example:

```
requirepass abc123
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl status redis-server
```

## 2. Security Group

Allow Redis **only** from Application EC2 SG on port **6379**.
In AWS Console → **EC2 → Security Groups**, edit inbound rules for the Redis instance:

| Type       | Protocol | Port | Source                           |
| ---------- | -------- | ---- | -------------------------------- |
| Custom TCP | TCP      | 6379 | SG-ID of your other EC2 instance |

⚠️ **DO NOT expose Redis to 0.0.0.0/0**

## 3. Test Connection

```bash
redis-cli -h <PUBLIC_IP> -p 6379 -a YOUR_PASSWORD
```
Example:

```bash
redis-cli -h 34.230.77.137 -p 6379 -a abc123
```

---

# 🐘 PostgreSQL Installation (Monitor Node)

## 1. Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl status postgresql
```

## 2. Create Database & User

```bash
sudo -i -u postgres
psql
CREATE USER db_user WITH PASSWORD 'db_pass';
CREATE DATABASE mydb OWNER db_user;
GRANT ALL PRIVILEGES ON DATABASE mydb TO db_user;
\q
```

## 3. Enable Remote Access

Edit:

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Set:

```
listen_addresses = '*'
```

Edit pg_hba.conf:

```bash
sudo nano sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add for same VPC access:

```
host    all     all     172.31.0.0/16     md5
```

Allow access from anywhere (ONLY if required):

```
host    all     all     0.0.0.0/0     md5
```
### 4. Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

### 5. Test PostgreSQL Connection

```bash
psql -h YOUR_PUBLIC_IP -U db_user -d mydb
```

Example:

```bash
psql -h 34.230.77.137 -U db_user -d mydb
```
---

# 🔥 Prometheus Installation (Monitor Node)

## 1. Create Prometheus User

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus /var/lib/prometheus
```

## 2. Install Prometheus

```bash
cd /tmp
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-amd64.tar.gz
tar xvf prometheus-2.53.0.linux-amd64.tar.gz
cd prometheus-2.53.0.linux-amd64
```

Move files:

```bash
sudo mv prometheus /usr/local/bin/
sudo mv promtool /usr/local/bin/

sudo mv consoles /etc/prometheus
sudo mv console_libraries /etc/prometheus
sudo mv prometheus.yml /etc/prometheus
```

Set permissions:

```bash
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
```

## 3. Prometheus Service

File:

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Contents:

```
[Unit]
Description=Prometheus Monitoring
After=network-online.target

[Service]
User=prometheus
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

## 4. Add Scrape Jobs

Edit:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add:

```yaml
- job_name: "expense_fastapi"
  metrics_path: "/metrics"
  static_configs:
    - targets: ["APP_SERVER_IP:8000"]
      labels:
        service: "expense-assistant"

- job_name: "node_exporter"
  static_configs:
    - targets: ["APP_SERVER_IP:9100"]
      labels:
        service: "node"
```

Restart Prometheus:

```bash
sudo systemctl daemon-reload
sudo systemctl restart prometheus
```
## 5. Security Group Rules

| Type       | Port | Source                |
| ---------- | ---- | --------------------- |
| Custom TCP | 9090 | your IP or trusted SG |

Access Prometheus:

```
http://<EC2_PUBLIC_IP>:9090
```
---

# 📊 Grafana Installation (Monitor Node)

## 1. Install Grafana

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana -y
```

Start service:

```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

Access Grafana:

```
http://<MONITOR_NODE_IP>:3000
```

Login: **admin / admin**

---
##  2. Add Firewall Rules

| Type       | Port | Source                |
| ---------- | ---- | --------------------- |
| Custom TCP | 3000 | your IP or trusted SG |

# 🔌 Add Prometheus as Data Source (Grafana)

1. Go to **Connections → Data Sources → Add Prometheus**
2. URL:

```
http://<MONITOR_NODE_IP>:9090
```

3. Save & Test

---

# 🖥️ Node Exporter Installation (Application Server)

## 1. Install Node Exporter

```bash
cd /tmp
curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
tar xvf node_exporter-1.8.2.linux-amd64.tar.gz
sudo mv node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/
```

Create service:

```bash
sudo nano /etc/systemd/system/node_exporter.service
```

Contents:

```
[Unit]
Description=Node Exporter
After=network-online.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

Test:

```bash
curl http://<APP_PRIVATE_IP>:9100/metrics
```

---

# 📊 Grafana Dashboards

## 1. Import Node Exporter Full Dashboard

Grafana → **Dashboards → Import** → enter:

```
1860
```

Shows:

* CPU, RAM, Disk
* Network I/O
* Filesystem
* Load Average

## 2. Import Custom Expense Assistant Dashboard

Paste dashboard JSON into Grafana Import.
Replace datasource `uid` before importing.

---

# 🚀 Deployment Ready

Your environment now includes:

* Redis (secured)
* PostgreSQL (remote‑enabled)
* Prometheus (with scrape configs)
* Grafana (visualization)
* Node Exporter (system metrics)
* Application metrics dashboard

System is fully production‑ready.
