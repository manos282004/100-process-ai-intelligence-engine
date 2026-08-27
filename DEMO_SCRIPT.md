# Final Demonstration Script

Target duration: 10–15 minutes.

## 1. Introduction and Assignment 2 overview — 45 seconds

“This is Assignment 2: the 100-Process AI Research & Intelligence Engine. It is a working application that turns enterprise process names into structured intelligence profiles using external research, Gemini analysis, validation, persistence, retrieval, and an executive dashboard.”

Show the Streamlit dashboard and briefly point out the Executive Overview, matrix, live analysis, and advisory console.

## 2. Problem statement — 45 seconds

“Large enterprises have hundreds or thousands of processes. The challenge is not just generating text; it is creating a repeatable, traceable pipeline that can research an unknown process, validate the result, persist it, find relationships, and remain responsive while work runs in the background.”

## 3. Mandatory architecture explanation — 60 seconds

Open `ARCHITECTURE.md` or show the diagram. Explain:

```text
Streamlit
  → FastAPI
  → async queue and workers
  → Wikipedia research
  → Gemini structured analysis
  → Pydantic validation
  → SQLite persistence
  → BM25 retrieval
  → dashboard/API output
```

Emphasize that Streamlit communicates with FastAPI over HTTP and does not contain the business pipeline.

## 4. Show 100 seeded processes — 45 seconds

In the dashboard, show the Process Intelligence Matrix and the Total processes metric.

Say: “The seed catalogue contains exactly 100 unique required processes: 20 each in Supply Chain, Finance, Customer/Retail, HR/Talent, and Legal/Compliance/Risk. These are Pending records only; the system does not fake completed intelligence.”

Optionally filter the matrix by name, such as `invoice` or `risk`.

## 5. Show SQLite persistence — 45 seconds

Show `process_intelligence.db` in the project folder. Use the API or a Python terminal query:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/stats
```

Explain that the database survives Streamlit refreshes, FastAPI restarts, and computer restarts. The exact 14-column `processes` schema is documented in `DATA_MODEL.md`.

## 6. Demonstrate asynchronous background processing — 60 seconds

Use the dashboard’s Queue pending work control with a small batch, such as 5. Or call:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/processes/queue-pending?limit=5"
```

Immediately refresh the dashboard. Point out that the request returns HTTP 202 and the UI remains responsive while the worker processes records. Show Pending, Processing, Analyzed, queue depth, and worker count changing from real backend state.

## 7. Explain orchestration and concurrency — 60 seconds

Say:

“FastAPI handles ingestion and returns immediately. The orchestration layer places IDs into an asyncio queue and coordinates each lifecycle. Workers perform Wikipedia research, call Gemini through a semaphore, validate the structured response, persist it, and refresh BM25. The default configuration uses three workers but only two concurrent Gemini calls, with request spacing and exponential backoff. A 100-record queue therefore does not create 100 simultaneous model calls.”

Point out the logs for queued, started, attempt, retry, completion, and failure events.

## 8. Demonstrate an analyzed process — 60 seconds

Select an Analyzed record in the matrix. Show all 11 dimensions:

1. Business purpose
2. Key activities
3. Current challenges
4. AI opportunity
5. Automation potential
6. Human involvement
7. Technologies
8. Business benefit
9. Risks
10. Evidence
11. Evidence URL

Click the Wikipedia evidence URL. Explain that invalid schema or evidence is never saved as a successful result.

## 9. Demonstrate BM25 executive search — 60 seconds

In the Executive Advisory Console, ask:

```text
Which processes have the highest automation potential?
```

Then ask:

```text
What are the biggest risks across finance and supply chain processes?
```

Explain the flow:

```text
Executive question
  → local BM25 retrieval over SQLite records
  → grounded context assembly
  → Gemini executive synthesis
  → answer plus retrieved process names
```

This is not a generic chatbot; the answer identifies the locally persisted records that informed it.

## 10. Perform the LIVE SURPRISE RECORD TEST — 30 seconds

Navigate to Live Process Analysis. Use a name that is not in the seed catalogue, for example:

```text
Drone-Assisted Core Audit
```

If that name was used previously, enter another unseen name such as:

```text
Autonomous Supplier Compliance Drone Review
```

## 11. Enter the previously unseen process — 20 seconds

Submit the name and point out the immediate acceptance message and record ID. Explain that the POST route has returned before Wikipedia or Gemini completes.

## 12. Show the live pipeline — 90 seconds

Refresh or allow dashboard polling to show the real state transition:

```text
Input
  → Pending
  → Processing
  → Wikipedia research
  → Gemini structured AI analysis
  → Pydantic validation
  → SQLite storage
  → BM25 refresh
  → Analyzed dashboard output
```

Show the resulting intelligence profile and click its evidence URL. Explain that the process name was not seeded or hardcoded and followed the same path as every other record.

## 13. Explain 1,000-process scalability — 60 seconds

“If the input grows from 100 to 1,000 processes, ingestion still only validates, writes, and queues IDs. The queue absorbs the burst. Worker concurrency is configurable, while the Gemini semaphore prevents an external API flood. Retries are bounded and backoff-protected. Pagination keeps API reads controlled, and Streamlit polls status rather than blocking on AI work. For production, SQLite can move to PostgreSQL and the local queue can move to Redis, RabbitMQ, or a worker broker without changing the pipeline contract.”

## 14. Explain free/open technology choices — 45 seconds

“The local application uses Python, FastAPI, Uvicorn, Pydantic, Streamlit, SQLite, Requests, and rank_bm25. Wikipedia is a public unauthenticated research API. Gemini is the only external hosted AI dependency and is configured through an environment variable. No paid software license, ORM, vector database, Docker, Kubernetes, or unnecessary framework is required.”

## 15. Final conclusion — 30 seconds

“This demonstrates a complete enterprise AI workflow: input, backend processing, external research, structured AI analysis, validation, persistence, retrieval, and output. It is responsive, traceable, dynamically extensible, and able to analyze an unknown Surprise Record without static responses.”

## Reset before the final demo

If old records exist, use a clean reset before starting the presentation:

```powershell
$env:RESET_DATABASE="true"
uvicorn app:app --reload
```

Verify:

```text
total 100 · pending 100 · analyzed 0 · failed 0 · processing 0
```

Then remove the flag before a normal restart:

```powershell
Remove-Item Env:RESET_DATABASE -ErrorAction SilentlyContinue
```

## Final judge checklist

- [ ] Working application
- [ ] Streamlit user interface
- [ ] FastAPI backend
- [ ] AI intelligence layer
- [ ] Data/knowledge layer
- [ ] External research/data
- [ ] Dynamic Surprise Record
- [ ] SQLite persistence
- [ ] 100 required seed records
- [ ] Async background workers
- [ ] Non-blocking API
- [ ] Queue orchestration
- [ ] Controlled concurrency
- [ ] Retry behavior
- [ ] Structured AI output
- [ ] Real evidence URL
- [ ] 1,000-process scalability explanation
- [ ] Free technology compliance
- [ ] No static mockup
- [ ] No hardcoded AI responses
