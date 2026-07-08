export type ExtensionMessage = {
  type: "VIDMIND_OPEN_SIDEBAR"
}

export function isExtensionMessage(value: unknown): value is ExtensionMessage {
  if (typeof value !== "object" || value === null) return false

  return "type" in value && value.type === "VIDMIND_OPEN_SIDEBAR"
}
