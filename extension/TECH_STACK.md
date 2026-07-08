# VidMind Extension Tech Stack

## Decision

VidMind will use a Vite-based Manifest V3 extension build. Phase 4 will replace
the current Plasmo scaffold with the following stack:

| Concern | Tool | Responsibility |
| --- | --- | --- |
| UI | React | Component composition and rendering |
| Language | TypeScript | Strict types across UI and extension messages |
| Build | Vite | Development server and production bundles |
| Extension build | CRXJS Vite Plugin | Manifest entries, content scripts, service worker, and HMR |
| Styling | Tailwind CSS | Utility styling backed by VidMind design tokens |
| Motion | Motion for React | Sidebar, message, and layout transitions |
| Icons | Lucide React | Consistent interface icons |
| Shared state | Zustand | Small typed stores without providers or reducers |

Redux is intentionally excluded.

## Package policy

Runtime dependencies:

- `react`
- `react-dom`
- `motion`
- `lucide-react`
- `zustand`

Development dependencies:

- `typescript`
- `vite`
- `@vitejs/plugin-react`
- `@crxjs/vite-plugin`
- `tailwindcss`
- `@tailwindcss/vite`
- `@types/chrome`
- `@types/react`
- `@types/react-dom`

The package lock is committed. Dependency versions are resolved and pinned by the
lockfile instead of using `latest` ranges. Production extension code must not load
scripts, fonts, or styles from a CDN.

## Why Vite and CRXJS

Vite provides the requested React and TypeScript development workflow. CRXJS adds
the extension-specific layer: it treats the Manifest V3 configuration as an entry
point, bundles the background service worker and content scripts, and supports
extension-aware development reloads.

This keeps the project close to standard Vite conventions without maintaining a
custom multi-entry Rollup configuration.

Phase 4 will perform the migration in one buildable change:

1. Move extension source under `src/` and the manifest under `public/`.
2. Add Vite, React, Tailwind, and CRXJS configuration.
3. Preserve the working YouTube trigger and side-panel shell.
4. Remove Plasmo dependencies and generated conventions.
5. Produce an unpacked extension in `dist/`.

## Architecture rules

### React

- Components are functions with explicitly typed props.
- Browser APIs stay in background, content, API, or hook modules—not presentational
  components.
- Component-local state stays in React. A Zustand store is introduced only when
  multiple sibling regions need the same state.

### TypeScript

- Strict mode is required.
- Extension message names and payloads use a shared discriminated union.
- Avoid `any`; boundary data is validated before entering UI state.
- `vite build` bundles TypeScript, while `tsc --noEmit` remains a separate required
  verification step.

### Tailwind CSS

- Tailwind utilities handle layout, spacing, typography, and interaction states.
- VidMind colors and reusable values live as CSS theme tokens rather than repeated
  arbitrary values.
- A small global stylesheet is allowed for resets, scrollbar treatment, and theme
  variables.
- No CSS-in-JS library is added.

### Motion

- Import the maintained Motion package from `motion/react`.
- Use Motion for component entry, exit, and layout changes.
- Keep simple color and border hover effects in CSS.
- All transforms respect `prefers-reduced-motion`.

### Lucide

- Import icons individually from `lucide-react` so unused icons are tree-shaken.
- Default visual size is 18 px with a 1.75 px stroke.
- Product identity continues to use the custom VidMind mark, not a Lucide glyph.

### Zustand

- Stores expose narrow selectors to avoid broad rerenders.
- Actions live beside the state they update.
- Server requests and Chrome APIs do not run implicitly during store creation.
- No persistence is added until a product requirement needs it.

## Build contract

```text
npm run dev        Start the extension-aware Vite development build
npm run typecheck  Run TypeScript without emitting files
npm run build      Typecheck and create the production extension in dist/
```

The initial browser target is Chromium 116 or newer because the shell uses
`chrome.sidePanel.open`. Firefox support remains a later compatibility task rather
than an implied Phase 3 guarantee.

## References

- [Vite documentation](https://vite.dev/guide/)
- [CRXJS content-script documentation](https://crxjs.dev/concepts/content/)
- [Tailwind CSS Vite installation](https://tailwindcss.com/docs/installation/using-vite)
- [Motion for React installation](https://motion.dev/docs/react-installation)
- [Zustand introduction](https://zustand.docs.pmnd.rs/learn/getting-started/introduction)
