chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch(console.error)
})

chrome.runtime.onMessage.addListener((message, sender) => {
  if (message?.type !== "VIDMIND_OPEN_SIDEBAR" || !sender.tab?.id) return

  chrome.sidePanel.open({ tabId: sender.tab.id }).catch((error) => {
    console.error("VidMind could not open the sidebar.", error)
  })
})
