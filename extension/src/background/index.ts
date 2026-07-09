import { isExtensionMessage } from "../utils/messages"

function openSidebarOrFallback(tabId: number) {
  if (chrome.sidePanel?.open) {
    chrome.sidePanel.open({ tabId }).catch((error: unknown) => {
      console.error("VidMind could not open the sidebar.", error)
    })
    return
  }

  chrome.tabs
    .create({ url: chrome.runtime.getURL("src/sidebar/index.html") })
    .catch((error: unknown) => {
      console.error("VidMind could not open the fallback view.", error)
    })
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel?.setPanelBehavior?.({ openPanelOnActionClick: true }).catch(console.error)
})

chrome.runtime.onMessage.addListener((message: unknown, sender) => {
  if (!isExtensionMessage(message) || !sender.tab?.id) return

  openSidebarOrFallback(sender.tab.id)
})
