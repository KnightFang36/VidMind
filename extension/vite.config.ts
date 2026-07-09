import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { crx } from "@crxjs/vite-plugin"
import { defineConfig } from "vite"
import manifest from "./public/manifest.json"

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    crx({ manifest }),
  ],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
})