import { Clock3 } from "lucide-react"
import { motion } from "motion/react"

import type { MessageSource } from "../types"

interface TimestampCardProps {
  source: MessageSource
  onClick?: (source: MessageSource) => void
}

export function TimestampCard({ source, onClick }: TimestampCardProps) {
  return (
    <motion.button
      className="inline-flex h-7 items-center gap-1.5 rounded-lg border border-[#2B3140] bg-[#171A21] px-2.5 text-[11px] font-medium text-[#AFC0F7] transition-colors hover:border-[#3E527F] hover:bg-[#1C2230] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4F7CFF]"
      type="button"
      onClick={() => onClick?.(source)}
      aria-label={`Jump to ${source.timestamp}${source.label ? `, ${source.label}` : ""}`}
      whileTap={{ scale: 0.97 }}
    >
      <Clock3 aria-hidden="true" size={12} strokeWidth={1.8} />
      {source.timestamp}
    </motion.button>
  )
}
