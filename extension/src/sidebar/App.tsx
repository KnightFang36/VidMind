import { useMemo, useState } from "react"

import { ChatInput } from "./components/ChatInput"
import { ChatWindow } from "./components/ChatWindow"
import { EmptyState } from "./components/EmptyState"
import { Header } from "./components/Header"
import type { ChatMessage } from "./types"
import "./styles/index.css"

export function App() {
  const [draft, setDraft] = useState("")
  const messages = useMemo<ChatMessage[]>(() => [], [])

  function handleSubmit() {
    if (!draft.trim()) return

    // Phase 8 will replace this placeholder with the local fake-chat flow.
    setDraft("")
  }

  return (
    <main className="flex h-dvh min-h-[420px] flex-col overflow-hidden bg-[#0F1115] text-[#F5F7FA]">
      <Header videoTitle="Open a YouTube video to begin" />

      <section className="min-h-0 flex-1 overflow-y-auto" aria-label="Conversation">
        {messages.length ? (
          <ChatWindow messages={messages} />
        ) : (
          <div className="flex min-h-full items-center justify-center py-8">
            <EmptyState onSuggestionSelect={setDraft} />
          </div>
        )}
      </section>

      <div className="composer-scrim shrink-0 pt-4">
        <ChatInput value={draft} onChange={setDraft} onSubmit={handleSubmit} />
      </div>
    </main>
  )
}
