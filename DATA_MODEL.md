# Data Model

## SQLite database

Database file:

```text
process_intelligence.db
```

Table:

```text
processes
```

The table uses the exact required 14 columns. No ORM is used; `app.py` uses Python’s built-in `sqlite3` with short-lived tracked connections, a busy timeout, and WAL mode.

## Required `processes` columns

| # | Column | SQLite type / constraint | Meaning |
|---:|---|---|---|
| 1 | `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Stable process identifier |
| 2 | `name` | `TEXT UNIQUE` | Enterprise process name; duplicate names are rejected |
| 3 | `status` | `TEXT DEFAULT 'Pending'` | Durable job outcome/state |
| 4 | `business_purpose` | `TEXT` | Why the process exists |
| 5 | `key_activities` | `TEXT` | Main activities in the process |
| 6 | `current_challenges` | `TEXT` | Operational pain points |
| 7 | `ai_opportunity` | `TEXT` | AI-enabled improvement opportunity |
| 8 | `automation_potential` | `TEXT` | Strictly `Low`, `Medium`, or `High` |
| 9 | `human_involvement` | `TEXT` | Human review, judgment, or exception role |
| 10 | `technologies` | `TEXT` | Relevant systems and technologies |
| 11 | `business_benefit` | `TEXT` | Expected business value |
| 12 | `risks` | `TEXT` | Implementation and operating risks |
| 13 | `evidence` | `TEXT` | Concise research-supported observation |
| 14 | `evidence_url` | `TEXT` | Verifiable Wikipedia source URL |

The Gemini response schema contains only the 11 intelligence columns from `business_purpose` through `evidence_url`. It does not include `id`, `name`, `status`, or other database metadata.

## Status lifecycle

Conceptually, the background job lifecycle is:

```text
Pending → Processing → Analyzed
Pending → Processing → Failed
```

`Processing` is transient live worker state returned as `display_status` and counted by `/stats`. The durable SQLite contract remains `Pending`, `Analyzed`, or `Failed`, preserving the required existing schema and avoiding a schema migration. Worker cleanup prevents a record from remaining permanently visible as Processing. Startup recovery also resets any legacy persisted Processing rows to Pending.

## Seed data

The application programmatically defines exactly 100 required process names and inserts them idempotently with `INSERT OR IGNORE`. The five domains are:

| Domain | Records |
|---|---:|
| Supply Chain & Logistics | 20 |
| Finance & Corporate Accounts | 20 |
| Customer Operations & Retail Excellence | 20 |
| Human Resources & Talent Pipelines | 20 |
| Legal, Compliance & Risk Governance | 20 |
| **Total** | **100** |

Seed records begin with `status = 'Pending'` and all intelligence fields empty. Seeding does not call Wikipedia or Gemini and does not create static AI results. The UI can queue selected Pending records through `POST /processes/queue-pending`.

## Dynamic records

A new Surprise Record is inserted into the same `processes` table, subject to the same unique `name` constraint and the same 11-field validated intelligence profile. No special hardcoded path exists for surprise names.

## Evidence integrity

The research component returns a retrieved Wikipedia context and a source URL. Gemini is instructed to copy that URL into `evidence_url`. Before persistence, the backend checks that the URL is HTTPS, belongs to Wikipedia, and matches the retrieved source URL. Invalid structured output or evidence fails the process rather than being saved as Analyzed.
