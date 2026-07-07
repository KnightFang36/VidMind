# UtubeChat

UtubeChat is an AI-powered browser extension for Chrome and Firefox that allows users to interact with YouTube videos through natural language. It extracts the video's transcript, builds a Retrieval-Augmented Generation (RAG) pipeline, and enables users to ask questions or generate summaries based on the video's content.

## Features

- Chat with any YouTube video using AI
- Generate summaries from video transcripts
- Context-aware question answering with RAG
- Semantic search over transcript chunks
- Support for Chrome and Firefox
- Fast and lightweight extension

## Tech Stack

### Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui
- WXT (Web Extension Framework)

### AI & RAG

- Vercel AI SDK
- LangChain
- OpenAI / Anthropic / Gemini APIs
- OpenAI Embeddings
- pgvector

### Backend

- Next.js API Routes
- PostgreSQL
- Prisma ORM
- Upstash Redis

### Deployment

- Vercel
- Neon PostgreSQL

## Project Structure

```text
utubeChat/
├── apps/
│   ├── extension/      # Browser extension
│   └── web/            # Landing page and API routes
├── packages/
│   ├── ai/             # RAG pipeline
│   ├── ui/             # Shared UI components
│   └── utils/          # Shared utilities
└── README.md
```

## Roadmap

- [ ] Set up the browser extension with WXT
- [ ] Extract YouTube transcripts
- [ ] Chunk transcript data
- [ ] Generate embeddings
- [ ] Implement the RAG pipeline
- [ ] Build the AI chat interface
- [ ] Add video summary generation
- [ ] Store chat history
- [ ] Support multiple AI models
- [ ] Optimize performance




## License

This project is licensed under the MIT License.

---

**Status:** Work in Progress