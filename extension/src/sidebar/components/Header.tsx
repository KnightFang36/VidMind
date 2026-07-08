import { Moon, Settings2 } from "lucide-react"

import { BrandMark } from "./BrandMark"

interface HeaderProps {
  videoTitle: string
  videoAvailable?: boolean
}

export function Header({ videoTitle, videoAvailable = false }: HeaderProps) {
  return (
    <header className="shrink-0 border-b border-[#262B36] bg-[#0F1115]/95 backdrop-blur-xl">
      <div className="flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-2.5">
          <BrandMark />
          <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#F5F7FA]">
            VidMind
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            className="icon-button"
            type="button"
            aria-label="Dark theme"
            title="Dark theme"
            disabled
          >
            <Moon aria-hidden="true" size={17} strokeWidth={1.75} />
          </button>
          <button
            className="icon-button"
            type="button"
            aria-label="Settings coming soon"
            title="Settings coming soon"
            disabled
          >
            <Settings2 aria-hidden="true" size={17} strokeWidth={1.75} />
          </button>
        </div>
      </div>

      <div className="border-t border-[#1B1F28] px-4 py-3.5">
        <div className="mb-1.5 flex items-center gap-2">
          <span className="text-[10px] font-semibold tracking-[0.09em] text-[#777F90] uppercase">
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
        <p
          className={`truncate text-[13px] leading-5 ${videoAvailable ? "font-medium text-[#DDE1E8]" : "text-[#777F90]"}`}
          title={videoTitle}
        >
          {videoTitle}
        </p>
      </div>
    </header>
  )
}
