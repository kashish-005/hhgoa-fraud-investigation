# HHGoa Fraud Investigation — Part 1

This is **Kashish's Part 1 foundation** for the Hacker House Goa 2026 TigerGraph Agentic Fraud Investigation task.

## What is included

- Original HHGOA_IEEE dataset
- Reproducible dataset-preparation scripts
- Prepared graph-ready CSVs
- TigerGraph schema
- TigerGraph loading jobs
- Basic GSQL investigation queries
- FastAPI backend with local-data mode
- TigerGraph client foundation
- Analyst dashboard foundation

## Part 1 boundary

Included:
- dataset integration
- card/customer preparation
- graph schema
- graph loading foundation
- basic graph investigation queries
- backend data APIs
- base analyst dashboard

Not included:
- AI agent orchestration
- GraphRAG implementation
- full TigerGraph MCP integration
- final next-best-action agent logic
- case-memory agent workflow
- 20-case automation
- final agent UI

Those belong to the second half of the team work.

## Dataset

The original files are in:

`data/raw/HHGOA_IEEE/`

Prepared graph-ready data is already included in:

`data/prepared/`

The README supplied with the dataset is preserved unchanged at:

`data/raw/HHGOA_IEEE/README.md`

## Run the backend locally

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open:

`http://127.0.0.1:8000/docs`

The backend uses the prepared CSVs by default, so it works without TigerGraph.

## Open the dashboard

The current Part 1 dashboard is:

`frontend/index.html`

It is intentionally a standalone HTML dashboard with no frontend build step.

For a quick local preview:

```bash
cd frontend
python3 -m http.server 5500
```

Open:

`http://127.0.0.1:5500`

The current dashboard is a visual foundation. Its placeholder evidence is deliberately marked as placeholder; the next implementation step is wiring it to the Part 1 APIs.

## Dataset preparation

The prepared CSVs are already included. If you ever need to rebuild them:

```bash
python3 dataset_prep/build_reference_data.py
python3 dataset_prep/build_transactions.py
```

## TigerGraph

1. Create a TigerGraph Savanna workspace or use Community Edition.
2. Run `graph/schema.gsql`.
3. Upload the files from `data/prepared/` to a location accessible to TigerGraph.
4. Run the loading jobs in `graph/loading_jobs.gsql`.
5. Install the queries under `graph/queries/`.
6. Test `get_customer_history` and `get_transaction_context` on a benchmark case.

The loading job uses `DEFINE FILENAME` placeholders because the exact accessible file path depends on the TigerGraph deployment.

## Important data rules

- `risk_score` is an input signal, not a verdict.
- The case pack contains 20 benchmark cases.
- Closed cases are the labeled investigation history.
- Device profiles use the composite `DeviceInfo|id_30|id_31|id_33` key with `UNK` placeholders for partial identity records.
- Some online transactions legitimately have no identity record.
- Card IDs are deterministically derived as `customer_id-K1`, `K2`, ... from sorted card2..card6 combinations.

## Next handoff

Keerti can continue from this folder by wiring the backend tools into the agent layer and adding the Part 2 investigation/decision workflow. Do not replace this foundation with a separate project.
