# Data Engineering Pipeline: E-Commerce Analytics

## Overview

This repository contains a production‑ready ELT pipeline for e‑commerce sales analytics. It orchestrates data generation, staging, transformation, quality validation, profiling, and monitoring using containerised services.

The pipeline is designed to be deployed locally with a single `docker-compose up` command and provides:

- Automated data generation (mock orders and line items)
- DBT‑based transformations (staging, intermediate, marts, and SCD Type 2 snapshots)
- Data quality checks via Great Expectations
- Profiling reports (Pandas Profiling / ydata‑profiling)
- Orchestration with Apache Airflow (CeleryExecutor)
- Observability stack: Prometheus, Grafana, Alertmanager, StatsD exporter
- PostgreSQL as the data warehouse

All credentials are managed via environment variables (`.env`) and never committed.

---

## Architecture

The system consists of the following services (Docker containers):

| Service               | Role                                                                 |
|-----------------------|----------------------------------------------------------------------|
| **PostgreSQL**        | Data warehouse; stores raw, transformed, and snapshot schemas        |
| **Redis**             | Message broker for Airflow CeleryExecutor                            |
| **Airflow**           | Orchestrator (webserver, scheduler, worker) with DBT & Python tasks  |
| **StatsD Exporter**   | Converts StatsD metrics to Prometheus format                         |
| **Prometheus**        | Metrics collection and storage                                       |
| **Postgres Exporter** | Exports PostgreSQL performance metrics to Prometheus                 |
| **Grafana**           | Dashboards for monitoring (pre‑configured data source)               |
| **Alertmanager**      | Routes alerts (e.g., to Telegram)                                    |
| **Adminer**           | Lightweight database UI                                              |

The DAG (`sales_pipeline`) executes daily:

1. Generates mock data into `raw` schema.
2. Runs Great Expectations validations on raw tables.
3. Executes DBT models (staging → intermediate → marts) and snapshots.
4. Runs DBT tests.
5. Generates DBT documentation.
6. Produces a profiling report for the `dim_customers` table.
7. Sends task duration metrics to StatsD.

Alerts are triggered on DAG failures and when tasks exceed thresholds (via Prometheus rules).

---

## Stack

| Component              | Technology                              |
|------------------------|-----------------------------------------|
| Data Warehouse         | PostgreSQL 14                           |
| Orchestration          | Apache Airflow 2.7 (CeleryExecutor)     |
| Transformations        | DBT Core 1.5 (Postgres adapter)         |
| Data Quality           | Great Expectations + dbt-expectations   |
| Data Profiling         | ydata‑profiling (pandas‑profiling)      |
| Monitoring             | Prometheus + Grafana + Alertmanager     |
| Metrics Exposition     | StatsD exporter, postgres‑exporter      |
| Containerisation       | Docker & Docker Compose                 |
| Language               | Python 3.10                             |
| Testing                | pytest (Airflow DAG tests)              |



## Getting Started

### Prerequisites

- Docker Engine ≥ 20.10 and Docker Compose ≥ 2.0
- Git
- (Optional) Make utility for convenience

### Installation

Clone the repository:

```bash
git clone https://github.com/your-org/data-engineering-project.git
cd data-engineering-project
Copy .env.example to .env and adjust variables:

bash
cp .env.example .env
# Edit .env with your own secrets (especially TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
Important: Do not commit .env to version control.

Build and start all services:

bash
docker-compose up -d --build
This will:

Build the Airflow image (with DBT, GE, etc.)

Start PostgreSQL, Redis, Prometheus, Grafana, Alertmanager, and other supporting services.

Initialise Airflow database.

(First run only) Initialise Great Expectations inside the Airflow container:

bash
docker exec -it data-engineering-project-airflow-1 bash
cd /opt/airflow
great_expectations init

# Create at least one expectation suite, e.g. for raw.orders
# Then exit
If you skip this step, the ge_validation task will fail.

Access the Airflow web UI at http://localhost:8080 (default credentials: airflow / airflow).

Enable and trigger the sales_pipeline DAG manually or wait for the scheduled run (daily at 08:00).

Monitoring & Alerting
Prometheus scrapes metrics from:

StatsD exporter (Airflow task durations, counts)

Postgres exporter (DB connections, table sizes, query performance)

(Optional) Airflow’s own metric endpoint if enabled

Grafana is pre‑configured with a Prometheus data source. Import community dashboards (e.g., Airflow dashboard ID 14782) or create your own.

Alertmanager sends notifications to Telegram. The configuration uses environment variables TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.

Default alert rules are defined in monitoring/prometheus/alerts.yml:

DAGNotRunning: fires if the pipeline hasn’t run in the last 24 hours.

TaskFailed: fires when any Airflow task fails.

Custom alerts can be added by modifying the Prometheus rules file.

Data Quality & Testing
DBT tests are defined in the tests/ directory inside the DBT project (not to be confused with the top‑level tests/). They ensure uniqueness, not‑null, accepted values, etc.

Great Expectations validates the raw data (raw.orders) before transformation. The validation script (run_ge_validation.py) is invoked as an Airflow task.

Profiling automatically generates a static HTML report for the dim_customers table using ydata‑profiling. Reports are saved to profiling/reports/.

Pipeline tests (pytest) verify DAG structure and dependencies. Run them inside the Airflow container:

bash
docker exec -it data-engineering-project-airflow-1 bash
pytest /opt/airflow/tests/
Development & Extending
Adding new DBT models
Place new .sql files in the appropriate directory under dbt/models/.

Update dbt_project.yml if you need custom materialisation settings.

Optionally add tests in dbt/tests/.

The DAG will automatically pick them up on the next run.

Adding a new data source
Extend generate_data.py to produce additional tables, or create a separate script to load external data.

Add new source definitions in dbt/models/staging/sources.yml.

Build staging models and reference them in intermediate/marts.

Changing alerting rules
Edit monitoring/prometheus/alerts.yml and restart Prometheus:

bash
docker-compose restart prometheus
Adding custom dashboards
Place your dashboard JSON files in monitoring/grafana/dashboards/ – they will be automatically provisioned.

Troubleshooting
Airflow webserver not starting: Check logs with docker-compose logs airflow. Ensure .env variables are correctly set.

Great Expectations validation fails: The expectation suite named orders_expectations must exist. Create it via the GE CLI inside the container.

Telegram alerts not received: Verify that TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are correct and that the bot has permission to send messages.

DBT run fails: Check the connection string; ensure the analytics schema exists (created automatically by DBT if not).




