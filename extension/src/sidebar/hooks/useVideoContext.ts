import { useEffect, useState } from "react"

import type { VideoContext } from "../types"

const STORAGE_KEY = "vidmind.videoContext"

const FALLBACK_CONTEXT: VideoContext = {
  videoId: "",
  title: "Open a YouTube watch page",
  available: false,
  url: "",
  transcriptStatus: "idle",
  updatedAt: 0
}

function isVideoContext(value: unknown): value is Partial<VideoContext> {
  return typeof value === "object" && value !== null
}

function normalizeContext(value: unknown): VideoContext {
  if (!isVideoContext(value)) return FALLBACK_CONTEXT

  const title = typeof value.title === "string" && value.title.trim()
    ? value.title.trim()
    : FALLBACK_CONTEXT.title

  const transcriptStatus =
    value.transcriptStatus === "loading" ||
    value.transcriptStatus === "ready" ||
    value.transcriptStatus === "unavailable"
      ? value.transcriptStatus
      : FALLBACK_CONTEXT.transcriptStatus

  return {
    videoId: typeof value.videoId === "string" ? value.videoId : FALLBACK_CONTEXT.videoId,
    title,
    available: Boolean(value.available),
    url: typeof value.url === "string" ? value.url : FALLBACK_CONTEXT.url,
    transcriptStatus,
    updatedAt:
      typeof value.updatedAt === "number" ? value.updatedAt : FALLBACK_CONTEXT.updatedAt
  }
}

function hasStorageSession() {
  return typeof chrome !== "undefined" && typeof chrome.storage?.session !== "undefined"
}

function isYouTubeWatchUrl(urlString: string) {
  try {
    const url = new URL(urlString)
    return (
      (url.hostname === "www.youtube.com" || url.hostname === "youtube.com") &&
      url.pathname === "/watch"
    )
  } catch {
    return false
  }
}

function extractVideoId(urlString: string) {
  try {
    const url = new URL(urlString)
    return url.searchParams.get("v")?.trim() ?? ""
  } catch {
    return ""
  }
}

function buildContextFromTab(tab: chrome.tabs.Tab): VideoContext | null {
  if (!tab.url || !isYouTubeWatchUrl(tab.url)) return null

  const title = typeof tab.title === "string" && tab.title.trim()
    ? tab.title.replace(/\s*-\s*YouTube\s*$/i, "").trim()
    : FALLBACK_CONTEXT.title

  return {
    videoId: extractVideoId(tab.url),
    title,
    available: true,
    url: tab.url,
    transcriptStatus: "idle",
    updatedAt: Date.now()
  }
}

export function useVideoContext() {
  const [context, setContext] = useState<VideoContext>(FALLBACK_CONTEXT)

  useEffect(() => {
    let cancelled = false

    async function syncFromActiveTab() {
      if (typeof chrome === "undefined" || !chrome.tabs?.query) return

      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (cancelled) return

        const tabContext = tabs.map(buildContextFromTab).find(Boolean) ?? null
        if (tabContext) {
          setContext(tabContext)
        }
      })
    }

    if (!hasStorageSession()) return

    chrome.storage.session.get(STORAGE_KEY, (items) => {
      setContext(normalizeContext(items[STORAGE_KEY]))
    })

    void syncFromActiveTab()

    const handleChange = (
      changes: { [key: string]: chrome.storage.StorageChange },
      areaName: string
    ) => {
      if (areaName !== "session") return

      const change = changes[STORAGE_KEY]
      if (!change) return

      setContext(normalizeContext(change.newValue))
    }

    const handleActivated = () => {
      void syncFromActiveTab()
    }

    const handleUpdated: Parameters<typeof chrome.tabs.onUpdated.addListener>[0] = (
      tabId,
      changeInfo,
      tab
    ) => {
      if (changeInfo.url || changeInfo.title || changeInfo.status === "complete") {
        const tabContext = buildContextFromTab(tab)
        if (tabContext) setContext(tabContext)
        if (!tabContext && tab.active) setContext(FALLBACK_CONTEXT)
      }
    }

    chrome.storage.onChanged.addListener(handleChange)
    chrome.tabs.onActivated.addListener(handleActivated)
    chrome.tabs.onUpdated.addListener(handleUpdated)

    return () => {
      cancelled = true
      chrome.storage.onChanged.removeListener(handleChange)
      chrome.tabs.onActivated.removeListener(handleActivated)
      chrome.tabs.onUpdated.removeListener(handleUpdated)
    }
  }, [])

  return context
}
