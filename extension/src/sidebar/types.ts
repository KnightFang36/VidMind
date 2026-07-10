export type MessageRole = "user" | "assistant"

export type TranscriptStatus = "idle" | "loading" | "ready" | "unavailable"

export interface MessageSource {
  id: string
  timestamp: string
  label?: string
  /** Deep link into the video at the cited moment (…watch?v=<id>&t=<sec>s). */
  url?: string
  /** Position of the cited moment, in seconds. */
  startSeconds?: number
  /** Transcript excerpt backing this citation. */
  snippet?: string
}

/** A single prior turn sent to the backend to enable conversation memory. */
export interface ConversationTurn {
  role: MessageRole
  content: string
}

export interface VideoContext {
  videoId: string
  title: string
  available: boolean
  url: string
  transcriptStatus: TranscriptStatus
  updatedAt: number
}

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  sources?: MessageSource[]
  /** False when the backend hallucination guard refused to answer. */
  grounded?: boolean
}