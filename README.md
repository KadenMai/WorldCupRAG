# World Cup RAG

A Retrieval-Augmented Generation system for FIFA World Cup match data.

Ask natural-language questions about tournaments. The system retrieves relevant match documents from ChromaDB and answers using a local Ollama model — grounded in your indexed data, not model memorization alone.

## Architecture

### Offline pipeline (indexing)

```text
Raw JSON
    │
Parser
    │
TournamentData
    │
DocumentBuilder
    │
Chunker
    │
EmbeddingClient
    │
VectorRepository
    │
ChromaDB (worldcup{year})
```

### Online pipeline (chat)

```text
User Question
    │
QueryService
    │
VectorRepository.search()
    │
PromptBuilder
    │
OllamaClient
    │
Answer + Sources
```

## Quick start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) running locally
- Models pulled:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

### Local setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
pip install -e .
```

Configure `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:1.5b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### Run the API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

### Docker

```bash
docker compose up --build
```

Services:

| Service    | URL                      |
|------------|--------------------------|
| API        | http://localhost:8000    |
| Ollama     | http://localhost:11434   |
| Open WebUI | http://localhost:3000    |

For Open WebUI, set the OpenAI-compatible base URL to:

`http://host.docker.internal:8000/v1`

and use model id `worldcup-rag`.

## Index a year

Data lives under `data/raw/{year}/` (for example `data/raw/2022/worldcup.json`).

### Via API

```text
POST /index/{year}
        │
        ▼
Load data/raw/{year}
        │
        ▼
Chunk
        │
        ▼
Embed
        │
        ▼
Create collection: worldcup{year}
        │
        ▼
(Optional) Activate
```

**Index and activate (default):**

```http
POST /index/2018
```

**Index without switching the active chat collection:**

```http
POST /index/2018?activate=false
```

**Example response:**

```json
{
  "year": 2018,
  "collection": "worldcup2018",
  "matches": 64,
  "documents": 64,
  "chunks": 64,
  "activated": true
}
```

### Via script

```bash
cd backend
python script/index_worldcup.py
```

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check + active year |
| `POST` | `/index/{year}` | Index a tournament year into `worldcup{year}` |
| `POST` | `/activate/{year}` | Switch chat to an already-indexed year |
| `POST` | `/chat` | RAG chat with answer + sources |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat (Open WebUI) |
| `GET` | `/v1/models` | List models for Open WebUI |

### Chat

```http
POST /chat
Content-Type: application/json

{
  "message": "Who won the World Cup?"
}
```

```json
{
  "answer": "Argentina won the 2022 FIFA World Cup...",
  "sources": [
    {
      "title": "Final: Argentina vs France",
      "score": 0.668
    }
  ]
}
```

### Activate another year

```http
POST /activate/2022
```

Chat then searches collection `worldcup2022`.

## Project layout

```text
WorldCupRAG/
├── backend/
│   ├── app/
│   │   ├── ingest/          # Parser, DocumentBuilder, Chunker, Indexer
│   │   ├── llm/             # Ollama chat + embedding clients
│   │   ├── models/          # Document, Chunk, SearchResult, ...
│   │   ├── rag/             # Query, Prompt, Chat, VectorRepository
│   │   └── main.py          # FastAPI
│   ├── script/              # Smoke tests + CLI indexer
│   └── requirements.txt
├── data/
│   ├── raw/{year}/          # Source JSON per tournament
│   └── chroma/              # Persistent ChromaDB (Docker)
└── docker-compose.yml
```

## Notes

- One match ≈ one document ≈ one chunk (v1).
- Each year gets its own Chroma collection: `worldcup2018`, `worldcup2022`, …
- Answers are grounded with a strict prompt; if context is missing, the model should say it doesn't know.
- Retrieval quality matters more than prompt tweaks — inspect logs for retrieved docs and the full prompt when debugging.
