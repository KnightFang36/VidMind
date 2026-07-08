import { ListChecks, MessageCircleQuestion, Sparkles } from "lucide-react"

interface EmptyStateProps {
  onSuggestionSelect: (suggestion: string) => void
}

const suggestions = [
  { label: "Summarize", icon: Sparkles },
  { label: "Key points", icon: ListChecks },
  { label: "Explain simply", icon: MessageCircleQuestion }
]

export function EmptyState({ onSuggestionSelect }: EmptyStateProps) {
  return (
    <div className="mx-auto flex w-full max-w-72 flex-col items-center px-4 text-center">
      <div className="mb-4 flex size-11 items-center justify-center rounded-2xl border border-[#2B3140] bg-[#171A21] text-[#86A2FF] shadow-[0_12px_32px_rgba(0,0,0,0.18)]">
        <Sparkles aria-hidden="true" size={20} strokeWidth={1.7} />
      </div>
      <h1 className="text-[15px] font-semibold tracking-[-0.015em] text-[#F5F7FA]">
        Ask anything about this video
      </h1>
      <p className="mt-2 text-xs leading-5 text-[#9299A8]">
        Explore ideas, clarify concepts, or get a concise overview.
      </p>

      <div className="mt-5 flex flex-wrap justify-center gap-2" aria-label="Example questions">
        {suggestions.map(({ label, icon: Icon }) => (
          <button
            className="suggestion-chip"
            type="button"
            key={label}
            onClick={() => onSuggestionSelect(label)}
          >
            <Icon aria-hidden="true" size={14} strokeWidth={1.8} />
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
