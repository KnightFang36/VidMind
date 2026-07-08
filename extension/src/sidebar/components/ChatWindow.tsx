import { useEffect, useRef } from "react"

import type { ChatMessage, MessageSource } from "../types"

import { Loading } from "./Loading"
import { Message } from "./Message"

interface ChatWindowProps {
  messages: ChatMessage[]
  loading?: boolean
  onSourceClick?: (source: MessageSource) => void
}

export function ChatWindow({
  messages,
  loading = false,
  onSourceClick
}: ChatWindowProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [loading, messages])

  return (
    <div className="flex flex-col gap-7 px-4 py-5" aria-live="polite">
      {messages.map((message) => (
        <Message key={message.id} message={message} onSourceClick={onSourceClick} />
      ))}
      {loading ? <Loading /> : null}
      <div ref={endRef} />
    </div>
  )
}
