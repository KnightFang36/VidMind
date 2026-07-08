import type { FormEvent } from "react"
import { useState } from "react"

import "./styles.css"

const API_URL = "http://localhost:8000/api/v1"

async function getActiveVideoId(): Promise<string> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  if (!tab.id) throw new Error("No active YouTube tab found.")

  const response = await chrome.tabs.sendMessage(tab.id, {
    type: "VIDMIND_GET_VIDEO_ID"
  })
  if (!response?.videoId) throw new Error("Open a YouTube video first.")
  return response.videoId
}

export function Sidebar() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)

  async function ask(event: FormEvent) {
    event.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setAnswer("")
    try {
      const videoId = await getActiveVideoId()
      const indexResponse = await fetch(`${API_URL}/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: videoId })
      })
      if (!indexResponse.ok) {
        const data = await indexResponse.json()
        throw new Error(data.detail ?? "VidMind could not index this video.")
      }
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: videoId, question })
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "VidMind could not answer.")
      setAnswer(data.answer)
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "Something went wrong.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>VidMind</h1>
      <p>Ask anything about the video.</p>
      <form onSubmit={ask}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Summarize the key ideas…"
        />
        <button disabled={loading}>{loading ? "Thinking…" : "Ask"}</button>
      </form>
      {answer && <section>{answer}</section>}
    </main>
  )
}
