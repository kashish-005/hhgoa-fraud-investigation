# HHGoa Fraud Investigation

An agentic fraud-investigation system built around **TigerGraph**, **Gemini**, and **FastAPI**.

The project combines transaction data, customer/card relationships, device and regional signals, historical closed fraud cases, graph-based investigation tools, and an AI investigation agent to support structured fraud-case analysis.

---

## Project Overview

HHGoa Fraud Investigation is designed to investigate flagged payment transactions by combining:

- Transaction-level risk signals
- Customer and card relationships
- Device and email-domain information
- Billing-region information
- Transaction history
- Historical closed fraud cases
- TigerGraph relationship traversal
- Gemini-powered investigation reasoning
- A FastAPI backend
- A browser-based investigation dashboard

The system is designed so that the model's `risk_score` is treated as an **input signal rather than a final fraud verdict**.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │   Fraud Case Pack   │
                    │    20 Benchmark     │
                    │       Cases         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │                     │
                    │ /api/cases          │
                    │ /api/transactions   │
                    │ /api/customers      │
                    │ /api/cards          │
                    │ /api/devices        │
                    │ /api/regions        │
                    │ /api/investigate    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌──────────────────┐
       │   TigerGraph    │          │   Gemini Agent   │
       │                 │          │                  │
       │ Customer        │          │ Investigation    │
       │ Card            │          │ Reasoning        │
       │ Transaction     │          │ Pattern          │
       │ Device          │          │ Risk/Confidence  │
       │ Email Domain    │          │ Next Actions     │
       │ Billing Region  │          │                  │
       │ Closed Case     │          │                  │
       └─────────────────┘          └──────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Investigation JSON  │
                    │                     │
                    │ Pattern             │
                    │ Risk level          │
                    │ Confidence          │
                    │ Evidence            │
                    │ Recommended actions │
                    │ SAR flag            │
                    └─────────────────────┘
````

---

## Repository Structure

```text
hhgoa-fraud-investigation/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── data_store.py
│       └── routers/
│           └── investigate.py
│
├── frontend/
│   └── index.html
│
├── graph/
│   └── schema.gsql
│
├── data/
│   ├── prepared/
│   │   ├── case_pack_prepared.csv
│   │   ├── transactions_core.csv
│   │   ├── cards.csv
│   │   ├── customers.csv
│   │   ├── device_profiles.csv
│   │   ├── closed_cases_core.csv
│   │   ├── closed_case_transactions.csv
│   │   └── closed_case_connected_cards.csv
│   └── raw/
│
├── cases/
│   ├── HHG-001.json
│   ├── HHG-002.json
│   ├── ...
│   └── HHG-020.json
│
├── agent.py
├── graph_tools.py
├── build_reference_data.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pandas
* Python-dotenv

### Graph

* TigerGraph
* pyTigerGraph
* Graph-based entity relationships

### AI

* Google Gemini
* `google-genai`
* Tool-using investigation agent

### Frontend

* HTML
* CSS
* JavaScript
* FastAPI-served dashboard

### Deployment

* Vercel
* GitHub

---

# Data Model

The graph contains the following major vertex types:

```text
Customer
Card
Transaction
DeviceProfile
EmailDomain
BillingRegion
ClosedCase
```

Relationships include:

```text
Customer ──OWNS──────────────> Card
Customer ──MADE──────────────> Transaction
Transaction ──FROM_DEVICE────> DeviceProfile
Transaction ──PURCHASER_EMAIL> EmailDomain
Transaction ──BILLED_IN──────> BillingRegion
Transaction ──NEXT_TRANSACTION> Transaction
ClosedCase ──INVOLVES────────> Transaction
ClosedCase ──ON_CARD─────────> Card
DeviceProfile ──CONNECTED_TO─> DeviceProfile
```

These relationships allow investigations to move beyond an individual transaction and examine connected entities and historical activity.

---

# Investigation Workflow

For each flagged case, the investigation process is:

1. Load the flagged transaction.
2. Identify the customer and card involved.
3. Examine transaction history.
4. Examine connected entities such as devices, email domains, and regions.
5. Search historical closed cases.
6. Identify a likely fraud pattern or determine that evidence is insufficient.
7. Assess risk and confidence.
8. Recommend next actions.
9. Produce a structured JSON investigation result.

The investigation agent is instructed to use graph evidence before reaching a final decision.

---

# AI Investigation Agent

The investigation agent is implemented in:

```text
agent.py
```

The agent uses Gemini with investigation tools for:

```text
get_transaction_history()
get_connected_entities()
get_prior_cases()
```

The agent is instructed to consider multiple evidence sources instead of treating the bank model's risk score as ground truth.

The expected investigation response has the following structure:

```json
{
  "case_id": "HHG-001",
  "pattern": "...",
  "risk_level": "low|medium|high",
  "confidence": "low|medium|high",
  "evidence_summary": "...",
  "reasoning": "...",
  "recommended_actions": [
    {
      "action": "...",
      "requires_approval": true
    }
  ],
  "sar_required": false,
  "explanation": "..."
}
```

Possible investigation actions include:

```text
allow
block_transaction
block_account
monitor_account
warn_customer
escalate_to_analyst
file_report
```

Actions that require human approval are explicitly marked in the output.

---

# Important Risk Principle

The `risk_score` is an **input signal, not a verdict**.

The investigation agent is expected to combine the model score with:

* Transaction context
* Customer reports
* Transaction history
* Device information
* Email information
* Regional information
* Historical closed cases
* Graph relationships

This helps avoid making a fraud decision based solely on a numerical model score.

---

# FastAPI API

The backend is implemented using FastAPI.

## Health

```http
GET /api/health
```

Returns:

```json
{
  "status": "ok",
  "mode": "local"
}
```

## Cases

```http
GET /api/cases
```

Returns the available investigation cases.

## Individual Case

```http
GET /api/cases/{case_id}
```

Example:

```http
GET /api/cases/HHG-001
```

## Transaction

```http
GET /api/transactions/{transaction_id}
```

## Customer History

```http
GET /api/customers/{customer_id}/history
```

## Card Transactions

```http
GET /api/cards/{card_id}/transactions
```

## Device Transactions

```http
GET /api/devices/{device_id}/transactions
```

## Region Transactions

```http
GET /api/regions/{region_id}/transactions
```

## AI Investigation

```http
POST /api/investigate
```

Request:

```json
{
  "case_id": "HHG-001"
}
```

The endpoint loads the case and passes it to the investigation agent.

---

# Dashboard

The frontend dashboard is served by FastAPI.

Local URL:

```text
http://127.0.0.1:8000/dashboard
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

The dashboard provides an interface for viewing investigation cases and connecting the frontend to the investigation API.

---

# Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/kashish-005/hhgoa-fraud-investigation.git
cd hhgoa-fraud-investigation
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file containing the required credentials/configuration for the graph and Gemini services.

Example:

```env
TG_HOST=<your-tigergraph-endpoint>
TG_TOKEN=<your-tigergraph-token>
GEMINI_API_KEY=<your-gemini-api-key>
```

Do not commit secrets to GitHub.

## 5. Start FastAPI

```bash
uvicorn backend.app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/dashboard
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# TigerGraph Setup

The graph schema is located at:

```text
graph/schema.gsql
```

The graph is designed around connected fraud entities rather than isolated transactions.

The investigation layer can query:

```text
Transaction history
Connected entities
Prior closed cases
```

The `graph_tools.py` module provides the graph-facing functions used by the investigation agent.

---

# Benchmark Cases

The benchmark contains **20 investigation cases**.

They are stored at the repository root in:

```text
cases/
```

with exactly one JSON file per case:

```text
HHG-001.json
HHG-002.json
HHG-003.json
...
HHG-020.json
```

These files contain the structured investigation outputs used for benchmark submission.

The case pack itself contains:

* Case ID
* Trigger type
* Trigger text
* Flagged transaction
* Card
* Customer
* Risk score
* Transaction amount
* Product category
* Channel
* Address/region information

Historical closed cases provide additional investigation context.

---

# Data Preparation

Prepared datasets are stored under:

```text
data/prepared/
```

The repository includes a preparation workflow for creating the reference tables used by the application.

The prepared data separates:

* Core transactions
* Customers
* Cards
* Device profiles
* Closed cases
* Historical case transactions
* Connected cards
* Benchmark case pack

Some online transactions legitimately do not have identity/device records, so missing identity information should not automatically be interpreted as fraud.

Device profiles use a composite representation of device characteristics.

---

# Deployment

The FastAPI application is configured for Vercel using:

```text
pyproject.toml
```

with the FastAPI entrypoint:

```text
backend.app.main:app
```

The application exposes:

```text
/
 /dashboard
 /docs
 /api/*
```

The production deployment should be configured with the required environment variables for any external Gemini or TigerGraph functionality.

---

# Current Project Status

### Implemented

* FastAPI backend
* Local prepared-data store
* Fraud investigation API routes
* Investigation dashboard
* TigerGraph graph schema
* Graph investigation helper functions
* Gemini investigation agent
* Structured investigation output
* Vercel deployment configuration
* 20 benchmark case answer files

### Investigation Components

```text
Case Pack
   ↓
FastAPI
   ↓
Graph Evidence + Historical Cases
   ↓
Gemini Investigation Agent
   ↓
Structured Investigation Decision
```

---

# Benchmark Submission

The benchmark submission repository is:

```text
https://github.com/kashish-005/hhgoa-fraud-investigation
```

The benchmark answer files are located in:

```text
cases/
```

and are named exactly:

```text
HHG-001.json
...
HHG-020.json
```

---

# Team

**HHGoa Fraud Investigation**

Built using:

* TigerGraph
* Gemini
* FastAPI
* Python
* Vercel

The project combines graph-based investigation with an AI agent to provide structured, evidence-driven fraud investigation workflows.
