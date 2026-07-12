# VidMind

VidMind is an AI-powered browser extension that lets you chat with any YouTube video in natural language. Its FastAPI backend extracts the transcript, builds a per-video **hybrid retrieval index** (semantic + keyword), and answers questions with a modern, citation-grounded RAG pipeline that links every answer back to the exact moment in the video.

---

[Under Development]

---

## Features

- **Chat with any YouTube video** through a sidebar UI.
- **Hybrid retrieval** — semantic (FAISS) + keyword (BM25) search fused with Reciprocal Rank Fusion.
- **Conversation memory** — follow-up questions are rewritten into standalone questions using chat history.
- **Cross-encoder reranking + context compression** for high-precision context.
- **Parent-document retrieval** — small chunks are searched, larger chunks are returned for richer context.
- **Timestamped citations** — every answer links back to the exact second in the video.
- **Hallucination guard** — refuses to answer when the transcript lacks supporting evidence.
- **Adaptive top-K** — retrieval depth scales with question difficulty.
- **Caching** — embeddings, retrieval results, and answers are cached (TTL + LRU) for speed and cost savings.
- **Streaming answers** via server-sent events.
- Works in Chrome and other Chromium-based browsers.

---

## Architecture

```text
┌──────────────────────────────┐         HTTP / JSON          ┌──────────────────────────────┐
│      Browser Extension        │  ─────────────────────────▶  │        FastAPI Backend        │
│                              │                              │                              │
│  content/  → detect video    │   POST /api/v1/index         │  routes/  → index, chat       │
│  sidebar/  → chat UI + cards │   POST /api/v1/chat          │  services/ → RAG pipeline     │
│  api/      → backend client  │  ◀─────────────────────────  │  data/     → FAISS + BM25     │
└──────────────────────────────┘     answer + citations       └───────────────┬──────────────┘
                                                                               │
                                                          ┌────────────────────┼────────────────────┐
                                                          ▼                    ▼                    ▼
                                                    ┌───────────┐       ┌────────────┐       ┌────────────┐
                                                    │  Groq LLM │       │ HuggingFace │       │  YouTube   │
                                                    │ inference │       │ embeddings  │       │ transcript │
                                                    └───────────┘       └────────────┘       └────────────┘
```

---

## RAG Pipeline

Every question flows through a multi-stage, memory-aware, citation-grounded pipeline:

```text
 Chat History + Question
          │
          ▼
 ┌─────────────────────────────────┐
 │ Standalone Question Generator    │  condense follow-ups using history (LLM)
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Adaptive Top-K                   │  pick retrieval depth from question difficulty
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Hybrid Retrieval (RRF)           │
 │  ┌───────────────┐  ┌──────────┐ │
 │  │ FAISS   (0.6) │  │ BM25(0.4)│ │
 │  │ semantic      │  │ keyword  │ │
 │  └───────┬───────┘  └────┬─────┘ │
 │          └── Reciprocal Rank ──┘ │
 │              Fusion              │
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ MultiQuery Expansion             │  LLM rephrases query for higher recall
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Cross-Encoder Rerank +           │  precision reranking + redundancy filter
 │ Context Compression              │
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Parent-Document Lookup           │  swap matched children for richer parents
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Hallucination Guard              │──▶ refuse if evidence is insufficient
 └───────────────┬─────────────────┘
                 ▼
 ┌─────────────────────────────────┐
 │ Prompt + LLM (streaming)         │
 └───────────────┬─────────────────┘
                 ▼
   Answer + Timestamped Citations
```

Embeddings, retrieval results, and final answers are cached throughout (TTL + LRU).

---

## Tech Stack

### Extension
- Vite + CRXJS
- React + TypeScript
- Tailwind CSS
- Motion (animations)
- Lucide React (icons)
- Zustand (state)

### Backend
- FastAPI + Uvicorn
- Pydantic

### AI & Retrieval
- LangChain (0.3.x)
- Groq — LLM inference
- Hugging Face embeddings — `BAAI/bge-large-en-v1.5`
- FAISS — dense vector search
- BM25 / `rank-bm25` — sparse keyword search
- Cross-encoder reranker — `cross-encoder/ms-marco-MiniLM-L-6-v2`
- `youtube-transcript-api` — transcript ingestion

---

## Backend Services

| File | Responsibility |
| --- | --- |
| `document_ingestion.py` | Fetch timestamped transcript segments and clean text |
| `embedding.py` | `bge-large` embeddings with a disk-backed embedding cache |
| `indexing.py` | Build and persist the hybrid FAISS + BM25 index and parent-document store |
| `retrieval.py` | Adaptive top-K, MultiQuery, cross-encoder rerank, context compression |
| `memory.py` | Conversation memory + standalone-question generation |
| `guardrails.py` | Hallucination guard + timestamped citation builder |
| `cache.py` | Thread-safe TTL/LRU caches for retrieval and answers |
| `rag.py` | End-to-end orchestration (sync + streaming) |

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- A **Groq API key** — free at [console.groq.com](https://console.groq.com)
- A Chromium-based browser (Chrome, Edge, Brave) for the extension

---

## Environment Variables

Create `backend/.env`:

```env
# REQUIRED — get from https://console.groq.com
GROQ_API_KEY=your_groq_api_key_here

# OPTIONAL — sensible defaults shown
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
EMBEDDING_DEVICE=cpu          # set to "cuda" if you have a GPU
```

No external keys are needed for retrieval — BM25, FAISS, embeddings, and the cross-encoder all run locally. Models download from Hugging Face on first use, so the first index build is slower while `bge-large` and the reranker are fetched.

---

## Getting Started

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# add your GROQ_API_KEY to backend/.env first, then:
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (docs at `/docs`).

### 2. Extension

```bash
cd extension
npm install
npm run build
```

Then load the extension:

1. Open `chrome://extensions`.
2. Enable **Developer mode** (top-right).
3. Click **Load unpacked** and select `extension/dist`.
4. Open any YouTube watch page and launch the VidMind sidebar.

For live development with hot reload, use `npm run dev` instead of `npm run build`.

---

## How It Works End-to-End

1. The content script detects the current YouTube video and passes its ID to the sidebar.
2. On first use, the extension calls `POST /api/v1/index`, which fetches the transcript and builds the hybrid FAISS + BM25 index (persisted to `data/faiss_indexes/`).
3. When you ask a question, the extension calls `POST /api/v1/chat` with your query and recent chat history.
4. The backend condenses history into a standalone question, retrieves and reranks the most relevant transcript chunks, guards against hallucination, and generates a grounded answer.
5. The answer is rendered with clickable timestamped source cards that jump to the exact moment in the video.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `GROQ_API_KEY` error on startup | Add the key to `backend/.env` and restart Uvicorn. |
| First request is very slow | Expected — Hugging Face models download on first use, then cache locally. |
| `422` on `/chat` | The video must be indexed first via `/api/v1/index`. |
| Dependency resolver conflicts | Install into a clean virtualenv; keep LangChain on the pinned `0.3.x` line (avoid `langgraph`/`langchain-classic` 1.x). |
| No transcript found | The video may have captions disabled; try another video. |

---

## License

This project is licensed under the MIT License.
