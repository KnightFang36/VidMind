import type { ChatMessage, MessageSource } from "../types"

import { BrandMark } from "./BrandMark"
import { TimestampCard } from "./TimestampCard"

interface MessageProps {
  message: ChatMessage
  onSourceClick?: (source: MessageSource) => void
}

export function Message({ message, onSourceClick }: MessageProps) {
  if (message.role === "user") {
    return (
      <article className="flex justify-end" aria-label="You">
        <div className="max-w-[88%] rounded-2xl rounded-br-md border border-[#2A3140] bg-[#171A21] px-3.5 py-2.5 text-[13px] leading-[1.55] text-[#E8EBF0]">
          {message.content}
        </div>
      </article>
    )
  }

  return (
    <article className="flex items-start gap-2.5" aria-label="VidMind">
      <BrandMark compact />
      <div className="min-w-0 flex-1 pt-0.5">
        <div className="whitespace-pre-wrap text-[13px] leading-[1.65] text-[#DDE1E8]">
          {message.content}
        </div>
        {message.sources?.length ? (
          <div className="mt-3">
            <p className="mb-2 text-[10px] font-semibold tracking-[0.08em] text-[#777F90] uppercase">
              Sources
            </p>
            <div className="flex flex-wrap gap-1.5">
              {message.sources.map((source) => (
                <TimestampCard
                  key={source.id}
                  source={source}
                  onClick={onSourceClick}
                />
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </article>
  )
}
