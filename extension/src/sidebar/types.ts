export type MessageRole = "user" | "assistant"

export interface MessageSource {
  id: string
  timestamp: string
  label?: string
}

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  sources?: MessageSource[]
}
