# Technology Inventory

## Runtime technologies

| Technology | Purpose in this project | License / availability |
|---|---|---|
| Python | Application language, async orchestration, SQLite integration, and runtime | Open-source Python; PSF License |
| FastAPI | REST API and application boundary | Open-source; MIT License |
| Uvicorn | ASGI server for FastAPI | Open-source; BSD-3-Clause License |
| Pydantic | Request validation and strict `ProcessIntelligence` structured-output validation | Open-source; MIT License |
| Streamlit | Enterprise dashboard and API-driven UI | Open-source; Apache License 2.0 |
| SQLite | Persistent local process registry in `process_intelligence.db` | Public domain software |
| `rank_bm25` | In-memory BM25 index over persisted process records | Open-source Python package; Apache-2.0 distribution |
| Requests | Wikipedia HTTP retrieval and dashboard-to-API HTTP calls | Open-source; Apache License 2.0 |
| Google GenAI SDK (`google-genai`) | Modern Python client for Gemini structured generation | Open-source SDK; Apache License 2.0 distribution |
| Wikipedia API | Unauthenticated search and page-context retrieval | Public API; no authentication required. Wikipedia content is available under its applicable Wikimedia licenses, including CC BY-SA for many articles |
| Google Gemini API | External AI generation using configurable `GEMINI_MODEL` (default `gemini-3.6-flash`) | External hosted AI service; availability, quotas, and any free-tier terms are subject to Google’s current service terms |

## Category distinction

### Open-source software libraries

Python, FastAPI, Uvicorn, Pydantic, Streamlit, SQLite, `rank_bm25`, Requests, and the Google GenAI SDK are software components installed locally from `requirements.txt` or provided by the Python runtime. They do not require a paid software license to reproduce this local project.

### Public/free external APIs

The Wikipedia API is unauthenticated and used for dynamic research. It is an external public data service, so network access and availability are required.

### External AI service dependency

Google Gemini is the project’s external intelligence provider. The API key is supplied through `GEMINI_API_KEY`; no key is stored in source code. The app isolates model calls in a provider function, uses structured JSON output, retries transient service failures, and marks unrecoverable failures rather than fabricating results.

## Replaceability and migration

The architecture keeps provider-specific behavior in the Gemini analysis and advisory-generation functions. The rest of the pipeline—Wikipedia research, Pydantic validation, SQLite persistence, BM25 retrieval, queue orchestration, and Streamlit/API presentation—does not depend on a specific model response implementation. A future local/open-source model or another approved provider can replace Gemini behind the same validated `ProcessIntelligence` boundary. Similarly, SQLite and the in-process queue are isolated replacement points for PostgreSQL and a durable distributed broker at larger scale.
