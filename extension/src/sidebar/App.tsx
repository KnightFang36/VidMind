import "./styles/index.css"

function VidMindMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M7 5.5 16.5 12 7 18.5v-13Z" fill="currentColor" />
        <path
          d="M17.5 5v14"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </span>
  )
}

export function App() {
  return (
    <main className="sidebar-shell">
      <div className="ambient-glow" />
      <section className="brand" aria-label="VidMind sidebar">
        <VidMindMark />
        <span>VidMind</span>
      </section>
    </main>
  )
}
