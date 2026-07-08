import { isExtensionMessage } from "../utils/messages"

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch(console.error)
})

chrome.runtime.onMessage.addListener((message: unknown, sender) => {
  if (!isExtensionMessage(message) || !sender.tab?.id) return

  chrome.sidePanel.open({ tabId: sender.tab.id }).catch((error: unknown) => {
    console.error("VidMind could not open the sidebar.", error)
  })
})
