// FIX: Original URL was /api/v1/chat — matched the fixed backend but original
// backend had no /v1 segment so all requests got 404.
// After fixing the backend router (prefix="/v1"), /api/v1/chat is now correct.
// Also fixed: FastAPI returns JSON {detail:...} for errors, not plain text.

/** A prior conversation turn, forwarded to enable backend conversation memory. */
export interface ChatHistoryTurn {
  role: "user" | "assistant"
  content: string
}

export interface ChatApiRequest {
  videoId: string
  query: string
  /** Optional prior turns so the backend can rewrite follow-ups into standalone questions. */
  history?: ChatHistoryTurn[]
}

/** New richer citation shape emitted by the hybrid RAG pipeline. */
export interface ChatApiSource {
  video_id?: string | null
  parent_id?: string | null
  chunk_index?: number | null
  start_seconds?: number | null
  timestamp?: string | null
  url?: string | null
  snippet?: string | null
}

export interface ChatApiResponse {
  video_id: string
  query: string
  answer: string
  sources?: ChatApiSource[]
  /** Question actually used for retrieval after history condensation. */
  standalone_question?: string | null
  /** False when the backend hallucination guard declined to answer. */
  grounded?: boolean
}

export interface IndexApiRequest {
  videoId: string
  force?: boolean
}

export interface IndexApiResponse {
  video_id: string
  chunks_indexed: number
}

const BASE_URL = "http://localhost:8000"
const CHAT_API_URL = `${BASE_URL}/api/v1/chat`
const INDEX_API_URL = `${BASE_URL}/api/v1/index`

async function parseErrorMessage(response: Response): Promise<string> {
  const text = await response.text()
  try {
    const json = JSON.parse(text) as { detail?: unknown }
    if (typeof json.detail === "string") return json.detail
    if (Array.isArray(json.detail)) {
      return (json.detail as Array<{ msg?: string }>)
        .map((e) => e.msg ?? String(e))
        .join("; ")
    }
  } catch {
    // not JSON
  }
  return text || `Request failed with status ${response.status}`
}

export async function sendChatRequest(payload: ChatApiRequest): Promise<ChatApiResponse> {
  const response = await fetch(CHAT_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_id: payload.videoId,
      query: payload.query,
      history: payload.history ?? [],
    }),
  })

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  return (await response.json()) as ChatApiResponse
}

export async function indexVideo(payload: IndexApiRequest): Promise<IndexApiResponse> {
  const response = await fetch(INDEX_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_id: payload.videoId,
      force: payload.force ?? false,
    }),
  })

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  return (await response.json()) as IndexApiResponse
}