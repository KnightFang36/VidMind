import { ArrowUp } from "lucide-react"
import { type FormEvent, type KeyboardEvent, useLayoutEffect, useRef } from "react"

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled?: boolean
  helperText?: string
}

const MAX_TEXTAREA_HEIGHT = 120

export function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
  helperText = "VidMind can make mistakes. Check important details."
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useLayoutEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = "auto"
    textarea.style.height = `${Math.min(textarea.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`
  }, [value])

  function submit(event?: FormEvent) {
    event?.preventDefault()
    if (!value.trim() || disabled) return
    onSubmit()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form className="px-3 pb-3" onSubmit={submit}>
      <div className="composer-card">
        <label className="sr-only" htmlFor="vidmind-question">
          Ask anything about this video
        </label>
        <textarea
          ref={textareaRef}
          id="vidmind-question"
          className="max-h-[120px] min-h-6 flex-1 resize-none overflow-y-auto bg-transparent text-[13px] leading-6 text-[#F5F7FA] outline-none placeholder:text-[#6F7786]"
          rows={1}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything…"
          disabled={disabled}
        />
        <button
          className="send-button"
          type="submit"
          disabled={disabled || !value.trim()}
          aria-label="Send question"
          title="Send"
        >
          <ArrowUp aria-hidden="true" size={17} strokeWidth={2} />
        </button>
      </div>
      <p className="mt-2 text-center text-[10px] leading-4 text-[#636B79]">
        {helperText}
      </p>
    </form>
  )
}
