import { useEffect, useRef } from "react"
import { AnimatePresence, motion } from "motion/react"

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
    <div className="flex flex-col gap-6 px-4 py-5" aria-live="polite">
      <AnimatePresence initial={false} mode="popLayout">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            layout
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
          >
            <Message message={message} onSourceClick={onSourceClick} />
          </motion.div>
        ))}
        {loading ? (
          <motion.div
            key="vidmind-loading"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
          >
            <Loading />
          </motion.div>
        ) : null}
      </AnimatePresence>
      <div ref={endRef} />
    </div>
  )
}
