export type MessageRole = "user" | "assistant"

export type TranscriptStatus = "idle" | "loading" | "ready" | "unavailable"

export interface MessageSource {
  id: string
  timestamp: string
  label?: string
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
}
