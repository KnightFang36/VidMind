const TRIGGER_HOST_ID = "vidmind-trigger-host"
const STORAGE_KEY = "vidmind.videoContext"

type TranscriptStatus = "idle" | "loading" | "ready" | "unavailable"

interface VideoContextState {
  videoId: string
  title: string
  available: boolean
  url: string
  transcriptStatus: TranscriptStatus
  updatedAt: number
}

const DEFAULT_CONTEXT: VideoContextState = {
  videoId: "",
  title: "Open a YouTube watch page",
  available: false,
  url: "",
  transcriptStatus: "idle",
  updatedAt: 0
}

let refreshToken = 0

function isWatchPage() {
  return window.location.hostname === "www.youtube.com" && window.location.pathname === "/watch"
}

function extractVideoId() {
  const url = new URL(window.location.href)
  const id = url.searchParams.get("v")?.trim()
  return id && id.length > 0 ? id : ""
}

function extractVideoTitle() {
  const heading = document.querySelector<HTMLHeadingElement>("h1")?.textContent?.trim()
  if (heading) return heading

  const title = document.title
    .replace(/\s*-\s*YouTube\s*$/i, "")
    .replace(/\s*\|\s*YouTube\s*$/i, "")
    .trim()

  return title || "YouTube video"
}

function updateStoredContext(context: VideoContextState) {
  chrome.storage.session.set({ [STORAGE_KEY]: context })
}

function createVidMindTrigger() {
  if (document.getElementById(TRIGGER_HOST_ID)) return document.getElementById(TRIGGER_HOST_ID)

  const host = document.createElement("div")
  host.id = TRIGGER_HOST_ID
  const shadowRoot = host.attachShadow({ mode: "open" })

  const style = document.createElement("style")
  style.textContent = `
    :host {
      all: initial;
    }

    button {
      align-items: center;
      background: #171a21;
      border: 1px solid #303645;
      border-radius: 999px;
      bottom: 28px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.34),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
      color: #f5f7fa;
      cursor: pointer;
      display: flex;
      font: 600 14px/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      gap: 9px;
      height: 44px;
      padding: 0 16px 0 11px;
      position: fixed;
      right: 24px;
      transition: border-color 160ms ease, box-shadow 160ms ease,
        transform 160ms ease;
      z-index: 2147483647;
    }

    button:hover {
      border-color: #4f7cff;
      box-shadow: 0 14px 36px rgba(0, 0, 0, 0.4),
        0 0 0 3px rgba(79, 124, 255, 0.14);
      transform: translateY(-2px);
    }

    button:active {
      transform: translateY(0) scale(0.98);
    }

    button:focus-visible {
      outline: 3px solid rgba(79, 124, 255, 0.5);
      outline-offset: 3px;
    }

    .mark {
      align-items: center;
      background: #4f7cff;
      border-radius: 50%;
      display: flex;
      height: 26px;
      justify-content: center;
      width: 26px;
    }

    svg {
      display: block;
      height: 15px;
      width: 15px;
    }

    @media (max-width: 600px) {
      button {
        bottom: 18px;
        padding-right: 11px;
        right: 14px;
      }

      .label {
        display: none;
      }
    }
  `

  const button = document.createElement("button")
  button.type = "button"
  button.title = "Open VidMind"
  button.setAttribute("aria-label", "Open VidMind sidebar")
  button.innerHTML = `
    <span class="mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M7 5.5 16.5 12 7 18.5v-13Z" fill="currentColor" />
        <path d="M17.5 5v14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>
    <span class="label">VidMind</span>
  `

  button.addEventListener("click", () => {
    chrome.runtime.sendMessage({ type: "VIDMIND_OPEN_SIDEBAR" }).catch((error: unknown) => {
      console.error("VidMind could not open the sidebar.", error)
    })
  })

  shadowRoot.append(style, button)
  document.documentElement.append(host)
  return host
}

function setTriggerVisibility(host: HTMLElement | null, visible: boolean) {
  if (!host) return
  host.style.display = visible ? "block" : "none"
}

async function refreshPageContext() {
  const token = ++refreshToken
  const host = document.getElementById(TRIGGER_HOST_ID)

  if (!isWatchPage()) {
    setTriggerVisibility(host, false)
    updateStoredContext(DEFAULT_CONTEXT)
    return
  }

  if (!host) createVidMindTrigger()
  setTriggerVisibility(document.getElementById(TRIGGER_HOST_ID), true)

  const context: VideoContextState = {
    videoId: extractVideoId(),
    title: extractVideoTitle(),
    available: true,
    url: window.location.href,
    transcriptStatus: "idle",
    updatedAt: Date.now()
  }

  updateStoredContext(context)
  console.info("VidMind: Video Found", context.title)
}

createVidMindTrigger()
void refreshPageContext()

window.addEventListener("yt-navigate-finish", () => {
  void refreshPageContext()
})

window.addEventListener("popstate", () => {
  void refreshPageContext()
})
