# VidMind

VidMind is an AI-powered browser extension that lets users interact with YouTube videos through natural language. Its FastAPI backend extracts a transcript, builds a per-video FAISS index, and answers questions using a RAG pipeline.

## Features

- Chat with any YouTube video using AI
- Generate summaries from video transcripts
- Context-aware question answering with RAG
- Semantic search over transcript chunks
- Support for Chrome and Firefox
- Fast and lightweight extension

## Tech Stack

### Extension

- Vite + CRXJS
- React
- TypeScript
- Tailwind CSS
- Motion
- Lucide React
- Zustand

### AI & RAG

- Vercel AI SDK
- LangChain
- Groq
- Hugging Face embeddings
- FAISS

### Backend

- FastAPI
- Pydantic

## Project Structure

```text
VidMind/
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/   # Chat and indexing endpoints
│   │   ├── core/            # Configuration
│   │   ├── schemas/         # Request and response models
│   │   ├── services/        # Transcript, embedding, indexing, and RAG
│   │   └── main.py          # FastAPI entry point
│   ├── tests/
│   └── requirements.txt
├── extension/
│   ├── public/manifest.json
│   ├── docs/
│   ├── src/
│   │   ├── background/
│   │   ├── content/
│   │   ├── sidebar/
│   │   ├── popup/
│   │   ├── api/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
uvicorn backend.app.main:app --reload
```

In another terminal:

```bash
cd extension
npm install
npm run dev
```

For a production build, run `npm run build`, then load `extension/dist` as an
unpacked extension in a Chromium-based browser.

## License

This project is licensed under the MIT License.

---

**Status:** Work in Progress
