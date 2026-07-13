import { ListChecks, MessageCircleQuestion, Sparkles } from "lucide-react"
import { motion } from "motion/react"

interface EmptyStateProps {
  onSuggestionSelect: (suggestion: string) => void
}

const suggestions = [
  {
    title: "Summarize this video",
    icon: Sparkles,
    prompt: "• Summarize this video .\n• Keep it detailed and accurate.\n• Highlight the main idea and conclusions at the end."
  },
  {
    title: "Generate Questions and Answers",
    icon: MessageCircleQuestion,
    prompt: "• Generate a question about the main idea of this video.\n• Provide a short answer (1-2 sentences).\n• Provide a long answer (3-5 sentences)."
  },
  {
    title: "Extract key moments",
    icon: ListChecks,
    prompt: "• List the key moments from this video.\n• Add timestamps when possible.\n• Show why each moment matters."
  }
]

export function EmptyState({ onSuggestionSelect }: EmptyStateProps) {
  return (
    <motion.div
      className="mx-auto flex w-full max-w-105 flex-col items-center px-4 text-center"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
    >
      <div className="mb-4 flex size-11 items-center justify-center rounded-2xl border border-[#2B3140] bg-[#171A21] text-[#86A2FF] shadow-[0_12px_32px_rgba(0,0,0,0.18)]">
        <Sparkles aria-hidden="true" size={20} strokeWidth={1.7} />
      </div>
      <h1 className="text-[15px] font-semibold tracking-[-0.015em] text-[#F5F7FA]">
        Ask anything about this video
      </h1>
      <p className="mt-2 text-xs leading-5 text-[#9299A8]">
        Use one of these starter prompts, then refine it with your own follow-up.
      </p>

      <div className="mt-5 grid w-full gap-2" aria-label="Example prompts">
        {suggestions.map(({ title, icon: Icon, prompt }) => (
          <button
            className="flex w-full items-start gap-3 rounded-2xl border border-[#262B36] bg-[#151820] px-3 py-3 text-left text-[#DDE1E8] transition-colors hover:border-[#3A465E] hover:bg-[#1A1E27]"
            type="button"
            key={title}
            onClick={() => onSuggestionSelect(prompt)}
          >
            <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-xl bg-[#1C2230] text-[#86A2FF]">
              <Icon aria-hidden="true" size={14} strokeWidth={1.8} />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-[12px] font-medium text-[#F5F7FA]">{title}</span>
              <span className="mt-1 block whitespace-pre-line text-[11px] leading-5 text-[#9299A8]">
                {prompt}
              </span>
            </span>
          </button>
        ))}
      </div>
    </motion.div>
  )
}
