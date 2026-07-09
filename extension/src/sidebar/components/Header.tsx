import { Settings2 } from "lucide-react"
import { AnimatePresence, motion } from "motion/react"
import { useEffect, useRef, useState } from "react"

import { BrandMark } from "./BrandMark"

interface HeaderProps {
  videoTitle: string
  videoAvailable?: boolean
  statusLabel: string
}

export function Header({
  videoTitle,
  videoAvailable = false,
  statusLabel
}: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handlePointerDown(event: PointerEvent) {
      if (!isMenuOpen) return
      if (menuRef.current?.contains(event.target as Node)) return
      setIsMenuOpen(false)
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setIsMenuOpen(false)
    }

    window.addEventListener("pointerdown", handlePointerDown)
    window.addEventListener("keydown", handleEscape)

    return () => {
      window.removeEventListener("pointerdown", handlePointerDown)
      window.removeEventListener("keydown", handleEscape)
    }
  }, [isMenuOpen])

  return (
    <header
      className="relative shrink-0 border-b backdrop-blur-xl"
      style={{
        borderColor: "var(--vidmind-border)",
        backgroundColor: "color-mix(in srgb, var(--vidmind-canvas) 95%, transparent)"
      }}
    >
      <div className="flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-2.5">
          <BrandMark />
          <span className="text-[15px] font-semibold tracking-[-0.02em]" style={{ color: "var(--vidmind-text)" }}>
            VidMind
          </span>
        </div>

        <div className="relative flex items-center gap-1.5" ref={menuRef}>
          <button
            className="icon-button"
            type="button"
            aria-label="Open settings"
            title="Settings"
            onClick={() => setIsMenuOpen((value) => !value)}
          >
            <Settings2 aria-hidden="true" size={17} strokeWidth={1.75} />
          </button>

          <AnimatePresence>
            {isMenuOpen ? (
              <motion.div
                className="absolute right-0 top-11 z-20 w-52 rounded-2xl border p-2 shadow-[0_20px_50px_rgba(0,0,0,0.38)]"
                style={{
                  borderColor: "var(--vidmind-border)",
                  backgroundColor: "var(--vidmind-surface)"
                }}
                initial={{ opacity: 0, y: -4, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -4, scale: 0.98 }}
                transition={{ duration: 0.16, ease: "easeOut" }}
                role="menu"
              >
                <p className="px-2 pb-2 text-[10px] font-semibold tracking-widest uppercase" style={{ color: "var(--vidmind-muted)" }}>
                  Theme
                </p>
                <div
                  className="flex items-center justify-between rounded-xl border px-3 py-2 text-[12px]"
                  style={{
                    borderColor: "var(--vidmind-border)",
                    backgroundColor: "color-mix(in srgb, var(--vidmind-canvas) 92%, transparent)",
                    color: "var(--vidmind-text)"
                  }}
                >
                  <span className="inline-flex items-center gap-2">
                    <span className="flex size-6 items-center justify-center rounded-lg text-[#86A2FF]" style={{ backgroundColor: "color-mix(in srgb, var(--vidmind-surface) 90%, transparent)" }}>
                      <Settings2 aria-hidden="true" size={13} strokeWidth={1.9} />
                    </span>
                    Dark
                  </span>
                  <span className="text-[11px]" style={{ color: "var(--vidmind-muted)" }}>Default</span>
                </div>
                <div className="mt-2 rounded-xl border border-dashed px-3 py-2 text-[11px] leading-5" style={{ borderColor: "var(--vidmind-border)", color: "var(--vidmind-muted)" }}>
                  More controls can live here later.
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>

      <div className="border-t px-4 py-3.5" style={{ borderColor: "var(--vidmind-border)" }}>
        <div className="mb-1.5 flex items-center gap-2">
          <span className="text-[10px] font-semibold tracking-[0.09em] uppercase" style={{ color: "var(--vidmind-muted)" }}>
            Current video
          </span>
          <span
            className={`size-1.5 rounded-full ${videoAvailable ? "bg-[#54C58A]" : "bg-[#555C6A]"}`}
            aria-hidden="true"
          />
          <span className="sr-only">
            {videoAvailable ? "Video found" : "No video detected"}
          </span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <p
            className={`min-w-0 flex-1 truncate text-[13px] leading-5 ${videoAvailable ? "font-medium" : ""}`}
            style={{ color: videoAvailable ? "var(--vidmind-text)" : "var(--vidmind-muted)" }}
            title={videoTitle}
          >
            {videoTitle}
          </p>
          <span
            className="shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-medium tracking-[0.04em]"
            style={{
              borderColor: videoAvailable ? "rgba(84,197,138,0.28)" : "var(--vidmind-border)",
              backgroundColor: videoAvailable
                ? "rgba(84,197,138,0.12)"
                : "color-mix(in srgb, var(--vidmind-surface) 96%, transparent)",
              color: videoAvailable ? "#8BE0AB" : "var(--vidmind-muted)"
            }}
          >
            {statusLabel}
          </span>
        </div>
      </div>
    </header>
  )
}
