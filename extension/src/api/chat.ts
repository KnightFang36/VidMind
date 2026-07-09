export interface ChatApiRequest {
  videoId: string
  query: string
}

export interface ChatApiResponse {
  video_id: string
  query: string
  answer: string
}

const CHAT_API_URL = "http://localhost:8000/api/v1/chat"

export async function sendChatRequest(payload: ChatApiRequest): Promise<ChatApiResponse> {
  const response = await fetch(CHAT_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      video_id: payload.videoId,
      query: payload.query
    })
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed with status ${response.status}`)
  }

  return (await response.json()) as ChatApiResponse
}