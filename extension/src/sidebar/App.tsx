import { useEffect, useRef, useState } from "react"
import { motion } from "motion/react"

import { ChatInput } from "./components/ChatInput"
import { ChatWindow } from "./components/ChatWindow"
import { EmptyState } from "./components/EmptyState"
import { Header } from "./components/Header"
import type { ChatMessage, MessageSource, VideoContext } from "./types"
import { useVideoContext } from "./hooks/useVideoContext"
import "./styles/index.css"

type AssistantTurn = {
  content: string
  sources: MessageSource[]
}

const assistantTurns: AssistantTurn[] = [
  {
    content:
      "Attention lets the model decide which tokens matter most at each step. Instead of treating every word equally, it builds a weighted context from the most relevant parts of the sequence.",
    sources: [
      { id: "src-1", timestamp: "00:32" },
      { id: "src-2", timestamp: "04:11" },
      { id: "src-3", timestamp: "09:15" }
    ]
  },
  {
    content:
      "CNNs detect local patterns by sliding learned filters across an image or signal. Early layers tend to find edges and textures, while deeper layers combine those features into higher-level structure.",
    sources: [
      { id: "src-4", timestamp: "01:05" },
      { id: "src-5", timestamp: "03:40" }
    ]
  },
  {
    content:
      "A useful way to think about this video is in three passes: what the model sees, how it prioritizes context, and where that context comes from. That keeps the explanation compact without losing the chain of reasoning.",
    sources: [
      { id: "src-6", timestamp: "02:18" },
      { id: "src-7", timestamp: "06:02" }
    ]
  }
]

export function App() {
  const videoContext = useVideoContext()
  const [draft, setDraft] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const turnIndexRef = useRef(0)
  const replyTimerRef = useRef<number | null>(null)

  useEffect(() => {
    setMessages([])
    setDraft("")
    setLoading(false)
    turnIndexRef.current = 0

    if (replyTimerRef.current !== null) {
      window.clearTimeout(replyTimerRef.current)
      replyTimerRef.current = null
    }
  }, [videoContext.url])

  useEffect(() => {
    return () => {
      if (replyTimerRef.current !== null) {
        window.clearTimeout(replyTimerRef.current)
      }
    }
  }, [])

  function handleSubmit() {
    if (!draft.trim() || loading || !videoContext.available) return

    const question = draft.trim()
    const response = assistantTurns[turnIndexRef.current % assistantTurns.length]
    const ragPayload = {
      query: question,
      videoId: videoContext.videoId,
      videoTitle: videoContext.title,
      videoUrl: videoContext.url
    }
    console.info("VidMind RAG payload", ragPayload)
    turnIndexRef.current += 1

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: question
      }
    ])
    setDraft("")
    setLoading(true)

    replyTimerRef.current = window.setTimeout(() => {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.content,
          sources: response.sources
        }
      ])
      setLoading(false)
      replyTimerRef.current = null
    }, 820)
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
      className="relative flex h-dvh min-h-105 flex-col overflow-hidden bg-[#0F1115] text-[#F5F7FA]"
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
          <div className="flex items-center justify-between gap-3 rounded-2xl border border-[#262B36] bg-[#151820] px-3 py-2.5">
            <div>
              <p className="text-[10px] font-semibold tracking-[0.09em] text-[#777F90] uppercase">
                Video ID
              </p>
              <p className="mt-0.5 text-[12px] leading-5 text-[#DDE1E8]">
                {videoContext.videoId || "Waiting for YouTube watch page"}
              </p>
            </div>
            <div className="text-right text-[11px] leading-4 text-[#7B8392]">
              <p>{videoContext.available ? "Ready for query grounding" : "Waiting for video"}</p>
              <p>Transcript fetch happens in RAG</p>
            </div>
          </div>
        </div>

        <section className="min-h-0 flex-1 overflow-y-auto" aria-label="Conversation">
          {messages.length || loading ? (
            <ChatWindow messages={messages} loading={loading} />
          ) : videoContext.available ? (
            <div className="flex min-h-full items-center justify-center px-4 py-8">
              <EmptyState onSuggestionSelect={setDraft} />
            </div>
          ) : (
            <div className="flex min-h-full items-center justify-center px-4 py-8 text-center">
              <div className="max-w-64 rounded-3xl border border-[#262B36] bg-[#171A21]/80 px-5 py-4 text-[13px] leading-6 text-[#9299A8] shadow-[0_14px_36px_rgba(0,0,0,0.16)] backdrop-blur-sm">
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
