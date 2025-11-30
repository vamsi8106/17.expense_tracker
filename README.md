# 🚀 Expense Tracker

## 📌 Project Overview

This project uses a **two-server AWS EC2 architecture** to deploy a production-ready application with full monitoring, CI/CD automation, and secure network communication.

### Overall Setup on EC2

![Complete setup](Images/complete.png)

Setup includes:

* **Application Server (app-node)** running Docker, Streamlit app, GitHub runner, and Node Exporter.
* **Monitoring Server (monitor-node)** running PostgreSQL, Redis, Prometheus, Grafana.
* **GitHub Actions CI/CD pipeline** deploying Docker images to **Amazon ECR** and auto-starting containers on EC2 via a self-hosted runner.

This document now also includes:

* Steps to create **IAM Role**
* Steps to create **ECR Repository**
* GitHub Secrets needed for CI/CD
* Permissions required for IAM user

---

# 🌐 EC2 Setup Summary

## EC2 1 — **Monitoring Server** (monitor-node)

Runs:

* PostgreSQL
* Redis
* Prometheus
* Grafana

## EC2 2 — **Application Server** (app-node)

Runs:

* Expense App (Docker container pulled from ECR)
* Node Exporter
* GitHub Self‑Hosted Runner

---

# 🛡️ AWS IAM, ECR & Security Setup

## 1️⃣ Create IAM User for GitHub Actions

Create an IAM user (example: `github-ci-user`).

### Required IAM Policies

Attach the following AWS-managed policies:

* `AmazonEC2ContainerRegistryFullAccess`
* `AmazonEC2FullAccess`
* `AmazonS3ReadOnlyAccess` (optional)
* `CloudWatchLogsFullAccess` (optional)

### Create Access Keys

Generate **Access Key ID** and **Secret Access Key** — use these in GitHub Secrets.

---

##  2️⃣ Create ECR Repository

Go to:
AWS Console → ECR → Create Repository

Example name: `expense-app-repo`

This will be referenced in GitHub Actions.

---

# 🔑 Security Groups

## monitor-node inbound rules

| Port | Service    | Source              |
| ---- | ---------- | ------------------- |
| 5432 | PostgreSQL | app-node private IP |
| 6379 | Redis      | app-node private IP |
| 9090 | Prometheus | Your IP (optional)  |
| 3000 | Grafana    | Your IP             |

## app-node inbound rules

| Port | Service       | Source                  |
| ---- | ------------- | ----------------------- |
| 8000 | API           | 0.0.0.0/0               |
| 8501 | Streamlit     | 0.0.0.0/0               |
| 9100 | Node Exporter | monitor-node private IP |
| 22   | SSH           | Your IP                 |

---

# 🛢️ Installation (monitor-node & app-node)

For the full local setup instructions, please see the detailed guide here:

👉 [Installation Guide](./Local_Installtion.md)

For the full setup instructions on EC2, please see the detailed guide here:

👉 [Installation Guide](./Installation.md)

⚠️ Initial Database Setup Required

Before starting the backend application for the first time, initialize your PostgreSQL schema using:

```bash
python3 -c "from src.utils.init_postgres import init_db; init_db()"
```
This ensures all required tables are created in PostgreSQL before the application begins serving requests.

# 🐳 Docker Installation (app-node)

```bash
sudo apt update -y
sudo apt install docker.io -y
sudo systemctl start docker
sudo usermod -aG docker ubuntu
newgrp docker
docker images
```
---

# 🤖 Install GitHub Runner (app-node)

Go to GitHub → Repository Settings → **Actions → Runners → New self‑hosted runner**.
Copy the commands and run them on the EC2 instance.

---

# 📝 .env file on app-node

Save at:

```
/home/ubuntu/expense.env
```

Content:

```
API_URL=http://APP_PRIVATE_IP:8000/chat
DATABASE_URL=postgresql+psycopg://db_user:db_pass@MONITOR_PRIVATE_IP:5432/expense_db
REDIS_HOST=MONITOR_PRIVATE_IP
REDIS_PORT=6379
REDIS_PASSWORD=yourpass
LOG_FILE=/app/logs/app.log
```


# 🤖 GitHub Secrets for CI/CD

You must add these in the repository:

| Secret Name             | Description                 |
| ----------------------- | --------------------------- |
| `AWS_ACCESS_KEY_ID`     | IAM user access key         |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key         |
| `AWS_REGION`            | Example: `us-east-1`        |
| `AWS_ACCOUNT_ID`        | From AWS console            |
| `ECR_REPOSITORY`        | Example: `expense-app-repo` |

Add secrets at:
**GitHub → Repo → Settings → Secrets → Actions → New secret**

---

# 🐳 GitHub Actions CI/CD (Push to ECR + Deploy)

Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy to ECR + EC2 (Using Access Keys)

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: self-hosted  # Your EC2 GitHub Runner

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Configure AWS Credentials (Access Keys)
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        run: |
          aws ecr get-login-password --region ${{ secrets.AWS_REGION }} \
          | docker login --username AWS --password-stdin \
              ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com

      - name: Build Docker Image
        run: |
          IMAGE="${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest"
          echo "Building image: $IMAGE"
          docker build -t $IMAGE .

      - name: Push Image to ECR
        run: |
          IMAGE="${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest"
          echo "Pushing image: $IMAGE"
          docker push $IMAGE

      - name: Deploy New Container on EC2
        run: |
          CONTAINER_NAME="expense_app_container"
          IMAGE="${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com/${{ secrets.ECR_REPOSITORY }}:latest"

          echo "Stopping old container..."
          docker stop $CONTAINER_NAME || true
          docker rm $CONTAINER_NAME || true

          echo "Pulling new image: $IMAGE"
          docker pull $IMAGE

          echo "Starting new container..."
          docker run -d \
            --name $CONTAINER_NAME \
            --env-file /home/ubuntu/expense.env \
            -v /home/ubuntu/logs:/app/logs \
            -p 8000:8000 \
            -p 8501:8501 \
            $IMAGE
```

---

# 📊 Grafana Dashboards
Grafana provides rich, interactive dashboards that allow real‑time visualization of system and application metrics collected from Prometheus and Node Exporter.
Once deployement is done we can see metric. Open Grafana at: *http://MONITOR_PUBLIC_IP:3000*

## 1️⃣ Built‑in Node Exporter Dashboard 

**Dashboard ID:** `1860`
**Name:** *Node Exporter Full*

Steps to import:

1. Grafana → *Dashboards → Import*
2. Enter ID **1860**
3. Select **Prometheus** datasource
4. Click **Import**

### Node Exporter Dashboard Screenshot

![Node Exporter Dashboard](Images/node_exporter_dashboard.png)

---

## 2️⃣ Custom Application Metrics Dashboard

Import your custom dashboard JSON:
**`monitoring/grafana-dashboard-expense-monitoring.json`**

### Custom Dashboard Screenshot

![Custom App Dashboard](Images/custom_app_dashboard.png)

---

# 🖼️ Application UI Screenshot

Below is your Streamlit UI screenshot:

![Streamlit UI](Images/streamlit_ui.png)

---

# 📚 References

* Prometheus Docs – [https://prometheus.io/docs/](https://prometheus.io/docs/)
* Grafana Docs – [https://grafana.com/docs/](https://grafana.com/docs/)
* Node Exporter – [https://github.com/prometheus/node_exporter](https://github.com/prometheus/node_exporter)
* Dashboard 1860 – [https://grafana.com/grafana/dashboards/1860-node-exporter-full/](https://grafana.com/grafana/dashboards/1860-node-exporter-full/)
* PostgreSQL Docs – [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
* Redis Docs – [https://redis.io/docs/](https://redis.io/docs/)
* AWS EC2 Docs – [https://docs.aws.amazon.com/ec2/](https://docs.aws.amazon.com/ec2/)

# 🎯 Conclusion

You can now have a complete, production-ready AWS EC2 deployment architecture with observability, CI/CD automation, secure networking, and scalable components. This setup follows cloud best practices and provides a strong foundation for future expansion.

Additionally, one can introduce a Load Balancer and scale horizontally by adding more EC2 instances behind it. For even more advanced scalability and reliability, moving to Kubernetes (EKS) allows better orchestration, autoscaling, and resilient service management.


