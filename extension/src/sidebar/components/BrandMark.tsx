interface BrandMarkProps {
  compact?: boolean
}

export function BrandMark({ compact = false }: BrandMarkProps) {
  const size = compact ? "size-6 rounded-[8px]" : "size-7 rounded-[9px]"
  const iconSize = compact ? "size-3.5" : "size-4"

  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center bg-[#4F7CFF] text-white shadow-[0_6px_18px_rgba(79,124,255,0.22)] ${size}`}
      aria-hidden="true"
    >
      <svg className={iconSize} viewBox="0 0 24 24" fill="none">
        <path d="M7 5.5 16.5 12 7 18.5v-13Z" fill="currentColor" />
        <path
          d="M17.5 5v14"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </span>
  )
}
