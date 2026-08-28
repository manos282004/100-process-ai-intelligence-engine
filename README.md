# Modus Enterprise AI Intelligence Engine

## Assignment 2 — 100-Process AI Research & Intelligence Engine

This project is a working enterprise process research and intelligence system. It accepts business process names, performs external Wikipedia research, sends the retrieved context to Google Gemini for structured analysis, validates the result with Pydantic, persists the intelligence in SQLite, refreshes a BM25 retrieval index, and presents the result through a Streamlit dashboard.

It is designed for the Modus Enterprise AI Build Challenge and supports both the required 100-process enterprise matrix and a completely new live Surprise Record.

## Key capabilities

- 100 required seed processes across five enterprise domains.
- Dynamic ingestion of previously unseen process names.
- Immediate FastAPI acceptance with HTTP 202.
- Long-running work handled by an `asyncio.Queue` and background workers.
- Controlled AI concurrency: up to three workers and two Gemini calls by default.
- Configurable request spacing and exponential backoff with jitter for transient Gemini failures.
- Real unauthenticated Wikipedia search and page-context retrieval.
- Gemini structured JSON generation using `ProcessIntelligence` and `response_mime_type="application/json"`.
- Pydantic validation before successful persistence.
- SQLite persistence in `process_intelligence.db`.
- BM25 search over persisted process intelligence.
- Executive advisory answers grounded in locally retrieved records.
- Retry endpoints for failed records and explicit database reset support.

## 100-process enterprise matrix

The seed catalogue contains exactly 100 unique names: 20 processes in each domain.

| Enterprise domain | Seed records |
|---|---:|
| Supply Chain & Logistics | 20 |
| Finance & Corporate Accounts | 20 |
| Customer Operations & Retail Excellence | 20 |
| Human Resources & Talent Pipelines | 20 |
| Legal, Compliance & Risk Governance | 20 |
| **Total** | **100** |

The names are defined as Python lists in `app.py`, checked for the exact 5 × 20 shape, and inserted with a unique constraint. Seeding creates only Pending records; it does not generate fake AI intelligence.

## Processing pipeline

```text
Process input
  → FastAPI validation and SQLite Pending record
  → asyncio.Queue
  → Wikipedia search and context retrieval
  → Gemini structured analysis
  → Pydantic validation and evidence URL validation
  → SQLite persistence as Analyzed or Failed
  → BM25 refresh
  → Streamlit/API output
```

The API ingestion route does not wait for Wikipedia or Gemini. The dashboard polls persisted API state and displays live worker state.

## Installation

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The required packages are listed in `requirements.txt`:

```text
fastapi
uvicorn
pydantic
google-genai
streamlit
requests
rank_bm25
python-dotenv
```

## Environment configuration

Required for live Gemini analysis:

```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
```

The configured model defaults to `gemini-3.6-flash` and can be overridden:

```powershell
$env:GEMINI_MODEL="gemini-3.6-flash"
```

Optional runtime controls:

```powershell
$env:WORKER_CONCURRENCY="3"
$env:AI_CONCURRENCY="2"
$env:QUEUE_MAX_SIZE="100"
$env:GEMINI_REQUEST_DELAY="1.0"
$env:GEMINI_MAX_ATTEMPTS="5"
$env:GEMINI_BACKOFF_BASE="2.0"
$env:GEMINI_BACKOFF_MAX="30.0"
$env:MODUS_API_URL="http://127.0.0.1:8000"
```

Wikipedia and Gemini require network access. The application logs the configured model and operational failures, but never logs the API key.

## Running the application

Start FastAPI from the project directory:

```powershell
uvicorn app:app --reload
```

Start Streamlit in a second terminal:

```powershell
streamlit run dashboard.py
```

Open the dashboard at the URL shown by Streamlit, normally `http://localhost:8501`.

Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Database reset

The database is normally persistent. To explicitly remove old test data and recreate exactly 100 Pending seed records:

```powershell
$env:RESET_DATABASE="true"
uvicorn app:app --reload
```

Confirm the dashboard or `GET /stats` reports:

```json
{
  "total": 100,
  "pending": 100,
  "analyzed": 0,
  "failed": 0,
  "processing": 0
}
```

Use the reset flag only for the intentional reset boot. Then stop the server and return to normal persistence:

```powershell
Remove-Item Env:RESET_DATABASE -ErrorAction SilentlyContinue
uvicorn app:app --reload
```

`reset_database()` closes tracked SQLite connections, removes the database and SQLite WAL/SHM sidecars when present, recreates the unchanged schema, seeds the required names idempotently, and refreshes BM25.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Database, Gemini readiness, worker, and queue health |
| GET | `/stats` | Real total, Pending, Processing, Analyzed, and Failed counts |
| GET | `/processes` | Paginated process registry; supports `status`, `limit`, `offset`, and `name` |
| GET | `/processes/{id}` | Full process intelligence record |
| GET | `/processes/by-name/{name}` | Retrieve a record by name |
| POST | `/processes` | Create a new Pending record and queue it; returns 202 |
| POST | `/processes/{id}/retry` | Retry one Pending or Failed record |
| POST | `/processes/queue-pending` | Queue a bounded Pending batch; for example `?limit=5` |
| POST | `/processes/retry-failed` | Reset and queue a bounded Failed batch |
| POST | `/load-test/processes` | Persist up to 1,000 Pending test records without calling Gemini by default |
| GET | `/search` | BM25 search over persisted process records |
| POST | `/chat` | BM25 retrieval followed by grounded Gemini advisory synthesis |

Example dynamic ingestion:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/processes `
  -ContentType "application/json" `
  -Body '{"name":"Drone-Assisted Core Audit"}'
```

The response is immediate. Poll `GET /processes/{id}` or refresh the dashboard to follow the real state.

For a safe ingestion/load demonstration, persist 1,000 Pending records without launching AI work:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/load-test/processes `
  -ContentType "application/json" `
  -Body '{"count":1000,"prefix":"Scalability Test Process","queue":false}'
```

Queue a small controlled batch afterward with `/processes/queue-pending?limit=5`.

## Testing and verification

Syntax checks:

```powershell
python -m py_compile app.py
python -m py_compile dashboard.py
```

Basic API checks while FastAPI is running:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/stats
Invoke-RestMethod "http://127.0.0.1:8000/processes?limit=5"
```

For a clean demonstration, reset first, verify 100 Pending records, then queue a small batch from the dashboard or:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/processes/queue-pending?limit=5"
```

## Scalability to 1,000 processes

The current local implementation is deliberately lightweight but has the correct control points:

- FastAPI inserts records and queues IDs without waiting for AI work.
- SQLite Pending rows provide a persistent backlog; the bounded `asyncio.Queue` absorbs bursts and a dispatcher drains deferred IDs as capacity becomes available.
- The semaphore prevents a 1,000-record batch from creating 1,000 simultaneous Gemini calls.
- Request pacing and retry backoff protect the external model service.
- SQLite persistence supports pagination and restart survival for the local challenge.
- BM25 is rebuilt from persisted records after successful analysis, so search uses actual stored intelligence.
- Streamlit performs controlled polling and does not own pipeline business logic.

For a larger production deployment, the isolated boundaries allow SQLite to move to PostgreSQL, the in-process queue to move to Redis/RabbitMQ/Celery/Dramatiq, and the local worker process to become a distributed worker pool. The current solution keeps the local build reproducible and explainable.

## Project files

- `app.py` — FastAPI, orchestration, queue workers, Wikipedia research, Gemini, Pydantic, SQLite, and BM25.
- `dashboard.py` — Streamlit presentation and HTTP API client.
- `requirements.txt` — Runtime dependencies.
- `process_intelligence.db` — Persistent local SQLite data created at runtime.
