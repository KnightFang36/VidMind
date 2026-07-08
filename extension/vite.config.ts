import { crx, type ManifestV3Export } from "@crxjs/vite-plugin"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

import manifest from "./public/manifest.json"

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    crx({ manifest: manifest as ManifestV3Export })
  ],
  build: {
    emptyOutDir: true,
    outDir: "dist"
  }
})
