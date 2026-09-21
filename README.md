# 🏎️ F1 Knowledge Chatbot

A Streamlit-based Formula 1 knowledge assistant built with retrieval-augmented
generation (RAG). It retrieves passages from a local Chroma collection and sends
the evidence to a Groq-hosted language model to answer questions with citations.

**Status: working local prototype.** The current knowledge collection contains
three curated driver profiles, not a complete or live F1 database.

## What works today

- Chat interface with session-scoped conversation history and a reset button.
- Historical profiles for Fernando Alonso, Lewis Hamilton, and Max Verstappen.
- Markdown ingestion with one searchable passage per `##` heading.
- Local embeddings using Chroma's default `all-MiniLM-L6-v2` model.
- Driver metadata filtering when a question identifies one supported driver.
- Deterministic handling of simple follow-ups such as “When did he win his first race?”
- Numbered answer citations, expandable source passages, and coverage dates.
- Search diagnostics showing the original question and the resolved search query.
- Instructions to acknowledge missing evidence instead of inventing an answer.
- Repeatable indexing that updates passages and removes stale generated entries.

## How it works

```text
Curated Markdown profiles → section-based passages → local embeddings → Chroma

User question → resolve driver context → retrieve evidence from Chroma
              → Groq answer generation → answer + citations in Streamlit
```

Embeddings and the vector database run locally. The question and retrieved
passages are sent to Groq for answer generation. Citation correctness and factual
grounding are prompted behavior, not independently verified guarantees.

## Tech stack

- Python 3.13+ and uv for environment and dependency management
- Streamlit for the chat interface
- Chroma for persistent local vector storage
- Groq serving `openai/gpt-oss-20b`, accessed through the OpenAI-compatible SDK
- python-dotenv for local configuration
- FastF1 and pandas for the separate, earlier race-results demo

An OpenAI API key is not required; the app uses a Groq API key.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```powershell
git clone https://github.com/gautamikh/F1-Knowledge-Chatbot.git
cd F1-Knowledge-Chatbot
uv sync --locked
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get a key from the [Groq Console](https://console.groq.com/keys). Never commit
credentials. Model availability, quotas, and costs depend on your provider account.

Build the local knowledge index:

```powershell
uv run python rag.py --index
```

The first run downloads the embedding model and requires internet access.
The three included profiles currently produce 12 passages. Generated vector
data is stored under `data/chroma/` and is intentionally excluded from Git.

Start the chatbot:

```powershell
uv run streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

Try this sequence:

1. “Which team did Fernando Alonso debut with?”
2. “When did he win his first race?”
3. Expand **Search diagnostics** to check that the follow-up names Alonso.
4. Expand **View retrieved passages and sources** to inspect the evidence.

## Knowledge collection

| Driver | Current historical coverage |
| --- | --- |
| Fernando Alonso | Selected facts through the 2021 season |
| Lewis Hamilton | Selected facts through the 2020 season |
| Max Verstappen | Selected facts through the 2024 season |

These are short, manually curated profiles with links to their original sources.
Coverage dates do not imply comprehensive biographies or up-to-date career totals.

To add knowledge, create a UTF-8 Markdown file in `data/knowledge/` using this
structure, replacing the placeholders with verified information:

```markdown
# Driver Name

Source: https://example.com/source-page
Checked on: YYYY-MM-DD
Coverage: Describe the period and topics covered.

## Career milestone

A short factual passage supported by the source above.
```

Keep sections short: the current chunker splits on headings, not token limits.
Run `uv run python rag.py --index` after adding, editing, or removing a profile.
This synchronizes the generated collection with the Markdown files.

New documents become searchable, but driver-aware filtering and follow-up memory
currently have separate hardcoded mappings in `rag.py` and `app.py`. Adding a file
alone does not extend those mappings. A shared driver registry is planned.

## Project layout

```text
app.py                       Streamlit RAG chatbot and driver-context handling
rag.py                       Markdown indexing, retrieval, and query CLI
race_results_app.py          Earlier FastF1 race-results chatbot
data/knowledge/              Versioned source profiles
data/chroma/                 Generated local vector index (ignored)
data/cache/                  FastF1 download cache (ignored)
scripts/test_fastf1.py       Manual FastF1 data-download smoke check
pyproject.toml               Python requirements and dependencies
uv.lock                     Locked dependency versions
.env                        Local Groq credentials (ignored)
```

## Manual checks

Inspect retrieval without making a Groq request:

```powershell
uv run python rag.py --query "When did Fernando Alonso win his first race?"
```

The retrieved evidence should include Alonso's first victory at the 2003
Hungarian Grand Prix. In the UI, also check:

- A named-driver question followed by a simple pronoun-based question.
- A topic switch from Alonso to Verstappen, followed by another question.
- A fresh conversation starting with “When did he win his first race?” — this
  should request clarification.
- An unsupported question such as “When did Charles Leclerc win his first F1
  race?” — the current collection cannot support an answer.

These are manual acceptance checks, not a measured accuracy benchmark. Automated
regression tests and a labeled evaluation dataset are still planned.

The earlier race-results demo remains available separately:

```powershell
uv run streamlit run race_results_app.py
```

It loads the 2025 Australian Grand Prix results through FastF1; it is not a live
results integration and is not connected to the RAG app.
<!-- 
## Known limitations

- Only three starter profiles; many historical questions are not covered.
- No live race feed, current standings, future calendar, or automatic source refresh.
- Follow-up handling is rule-based and limited to supported driver names and
  simple phrasing; it is not general conversational understanding.
- Similarity search can return irrelevant passages, especially for unsupported drivers.
- There is no reranker, relevance threshold, or automated citation verifier yet.
- Chat history lives only in the current Streamlit session.
- This is a local prototype, without production authentication, monitoring, or
  multi-user deployment hardening.

## Roadmap — not implemented yet

1. Add a shared driver registry with stable IDs and aliases, using Jolpica-F1.
2. Expand sourced biographies through a repeatable ingestion pipeline with
   provenance, coverage tracking, and token-aware chunking.
3. Store historical results and statistics in SQL for exact lookups and calculations.
4. Add refreshable standings and future race schedules with visible timestamps.
5. Integrate a live-session data provider, subject to access terms and licensing.
6. Route questions to document retrieval, SQL, or live data as appropriate.
7. Add automated regression tests, retrieval/answer evaluations, and latency/cost tracking.
8. Package and deploy the application with persistent storage and operational safeguards.

The intended design is hybrid: narrative knowledge belongs in the vector index;
results, standings, and schedules belong in structured storage. Live data needs
explicit freshness tracking rather than being treated as static knowledge. -->

## Sources and attribution

Each profile records its source URL, checked date, and historical coverage.
Source material remains subject to its respective owners' terms. Review source
licenses before expanding ingestion or redistributing content. This is an
independent educational project and is not affiliated with Formula 1, its teams,
or the referenced data providers.
