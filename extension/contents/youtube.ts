const VIDEO_ID_PATTERN = /^[a-zA-Z0-9_-]{11}$/

function currentVideoId(): string | null {
  const videoId = new URL(window.location.href).searchParams.get("v")
  return videoId && VIDEO_ID_PATTERN.test(videoId) ? videoId : null
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "VIDMIND_GET_VIDEO_ID") {
    sendResponse({ videoId: currentVideoId() })
  }
})
