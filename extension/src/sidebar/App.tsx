import { useEffect, useState } from "react"
import { motion } from "motion/react"

import { sendChatRequest } from "../api/chat"
import type { ChatApiSource, ChatHistoryTurn } from "../api/chat"
import { ChatInput } from "./components/ChatInput"
import { ChatWindow } from "./components/ChatWindow"
import { EmptyState } from "./components/EmptyState"
import { Header } from "./components/Header"
import { useVideoContext } from "./hooks/useVideoContext"
import type { ChatMessage, MessageSource, VideoContext } from "./types"
import "./styles/index.css"

// Only send the last few turns so the backend memory prompt stays small.
const MAX_HISTORY_TURNS = 6

function buildHistory(messages: ChatMessage[]): ChatHistoryTurn[] {
  return messages
    .slice(-MAX_HISTORY_TURNS)
    .map((message) => ({ role: message.role, content: message.content }))
}

function buildPayload(
  videoContext: VideoContext,
  query: string,
  history: ChatHistoryTurn[]
) {
  return {
    videoId: videoContext.videoId,
    query,
    history
  }
}

// Map the backend citation objects into the UI's MessageSource shape.
function mapSources(sources: ChatApiSource[] | undefined): MessageSource[] {
  if (!sources?.length) return []
  return sources
    .filter((source) => source.timestamp || source.snippet)
    .map((source, index) => ({
      id: `${source.parent_id ?? source.chunk_index ?? index}`,
      timestamp: source.timestamp ?? "0:00",
      label: source.snippet ?? undefined,
      url: source.url ?? undefined,
      startSeconds: source.start_seconds ?? undefined,
      snippet: source.snippet ?? undefined
    }))
}

export function App() {
  const videoContext = useVideoContext()
  const [draft, setDraft] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setMessages([])
    setDraft("")
    setLoading(false)
  }, [videoContext.url])

  async function handleSubmit() {
    if (!draft.trim() || loading || !videoContext.available) return

    const query = draft.trim()
    const history = buildHistory(messages)
    const payload = buildPayload(videoContext, query, history)
    console.info("VidMind request payload", payload)

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: query
      }
    ])
    setDraft("")
    setLoading(true)

    try {
      const response = await sendChatRequest(payload)
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          sources: mapSources(response.sources),
          grounded: response.grounded ?? true
        }
      ])
    } catch (error) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content:
            error instanceof Error
              ? `Backend request failed: ${error.message}`
              : "Backend request failed."
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const videoTitle = videoContext.available ? videoContext.title : "Open a YouTube watch page"
  const statusLabel = videoContext.available
    ? videoContext.videoId
      ? "Video found"
      : "Video detected"
    : "No video"
  const helperText = videoContext.available
    ? "VidMind can make mistakes. Check important details."
    : "Open a YouTube watch page to start chatting."

  return (
    <motion.main
      className="relative flex h-dvh min-h-105 flex-col overflow-hidden"
      style={{
        backgroundColor: "var(--vidmind-canvas)",
        color: "var(--vidmind-text)"
      }}
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-100"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(circle at top left, rgba(79,124,255,0.14), transparent 34%), radial-gradient(circle at top right, rgba(79,124,255,0.08), transparent 26%), linear-gradient(to bottom, rgba(255,255,255,0.01), transparent 18%)"
        }}
      />

      <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden">
        <Header
          videoTitle={videoTitle}
          videoAvailable={videoContext.available}
          statusLabel={statusLabel}
        />

        <div className="border-b border-[#1B1F28] px-4 py-3">
          <div
            className="flex items-center justify-between gap-3 rounded-2xl border px-3 py-2.5"
            style={{
              borderColor: "var(--vidmind-border)",
              backgroundColor: "color-mix(in srgb, var(--vidmind-surface) 92%, transparent)"
            }}
          >
            <div>
              <p
                className="text-[10px] font-semibold tracking-[0.09em] uppercase"
                style={{ color: "var(--vidmind-muted)" }}
              >
                Video ID
              </p>
              <p className="mt-0.5 text-[12px] leading-5" style={{ color: "var(--vidmind-text)" }}>
                {videoContext.videoId || "Waiting for YouTube watch page"}
              </p>
            </div>
            <div className="text-right text-[11px] leading-4" style={{ color: "var(--vidmind-muted)" }}>
              <p>{videoContext.available ? "Ready for query grounding" : "Waiting for video"}</p>
              <p>Transcript fetch happens in RAG</p>
            </div>
          </div>
        </div>

        <section className="min-h-0 flex-1 overflow-y-auto" aria-label="Conversation">
          {messages.length || loading ? (
            <ChatWindow
              messages={messages}
              loading={loading}
              onSourceClick={(source) => {
                if (source.url) {
                  window.open(source.url, "_blank", "noopener,noreferrer")
                }
              }}
            />
          ) : videoContext.available ? (
            <div className="flex min-h-full items-center justify-center px-4 py-8">
              <EmptyState onSuggestionSelect={setDraft} />
            </div>
          ) : (
            <div className="flex min-h-full items-center justify-center px-4 py-8 text-center">
              <div
                className="max-w-64 rounded-3xl border px-5 py-4 text-[13px] leading-6 shadow-[0_14px_36px_rgba(0,0,0,0.16)] backdrop-blur-sm"
                style={{
                  borderColor: "var(--vidmind-border)",
                  backgroundColor: "color-mix(in srgb, var(--vidmind-surface) 80%, transparent)",
                  color: "var(--vidmind-muted)"
                }}
              >
                Open a YouTube watch page to bring the sidebar to life.
              </div>
            </div>
          )}
        </section>

        <div className="composer-scrim shrink-0 pt-4">
          <ChatInput
            value={draft}
            onChange={setDraft}
            onSubmit={handleSubmit}
            disabled={!videoContext.available}
            helperText={helperText}
          />
        </div>
      </div>
    </motion.main>
  )
}