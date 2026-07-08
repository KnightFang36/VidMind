# VidMind Sidebar Design

## Product feel

VidMind should feel focused, calm, and native to a serious research workflow. The
visual density sits between Cursor Chat and Notion AI, while source treatment is
inspired by Perplexity. It should not look like a miniature marketing page.

Design principles:

1. Keep the video context visible without competing with the conversation.
2. Make the next action obvious: ask a question about the current video.
3. Use depth sparingly. Borders and tonal changes separate surfaces; shadows are
   reserved for the composer and temporary overlays.
4. Prefer concise labels, compact controls, and generous message spacing.
5. Keep all primary actions reachable at a sidebar width of 320 px.

## Layout

```text
┌──────────────────────────────────┐
│ [V] VidMind             [⚙] [×] │  56 px header
├──────────────────────────────────┤
│ CURRENT VIDEO                    │
│ How Transformers Work        •   │  68 px context strip
├──────────────────────────────────┤
│                                  │
│                                  │
│       Conversation area          │  flexible, scrollable
│                                  │
│                                  │
│  ┌────────────────────────────┐  │
│  │ Ask anything…              │  │
│  │                       [↑]  │  │  anchored composer
│  └────────────────────────────┘  │
│  AI can make mistakes.           │
└──────────────────────────────────┘
```

The shell is a three-row grid: fixed header, fixed video context, and a flexible
conversation region. The composer stays anchored to the bottom while only the
message history scrolls. Content has 16 px horizontal padding and remains usable
from 300 px to 520 px wide.

## Regions

### Header

- Left: 28 px VidMind mark and wordmark.
- Right: icon-only settings and close controls with tooltips.
- A subtle bottom border separates navigation from video context.
- Settings opens a small menu; theme is a row inside that menu rather than a
  permanent header control.

### Current video

- Uppercase 10 px eyebrow: `CURRENT VIDEO`.
- One-line title with ellipsis and a small status dot.
- Status text is exposed to assistive technology: `Video found`, `No video`, or
  `Reading transcript`.
- The strip may become a compact two-line card later, but never shows a thumbnail;
  the YouTube page already provides that visual context.

### Empty state

- Centered vertically in the available conversation space, slightly above true
  center to leave visual room for the composer.
- A restrained wave icon, a one-line invitation, and three suggestion chips:
  `Summarize`, `Key points`, and `Explain simply`.
- Suggestions fill the composer when selected; they do not send immediately.

### Conversation

- Messages use a single-column transcript, not opposing speech bubbles.
- User messages have a compact tinted surface aligned to the right.
- Assistant messages use the page background with a small VidMind mark and wider
  readable line length.
- Sources appear directly below the assistant answer as timestamp pills. A source
  click will seek the YouTube player in a later phase.
- Consecutive messages have 20 px separation; a new turn has 28 px separation.

### Composer

- Rounded 14 px card with a textarea and one circular send button.
- Textarea grows from one to five lines, then scrolls internally.
- `Enter` sends and `Shift+Enter` inserts a newline.
- Disabled, focused, and loading states must be visually distinct.
- The composer is separated from messages by a soft top gradient, not a hard bar.

## Visual system

### Color roles

| Role | Value | Usage |
| --- | --- | --- |
| Canvas | `#0F1115` | Sidebar background |
| Surface | `#171A21` | Composer, user message, menus |
| Border | `#262B36` | Dividers and control outlines |
| Accent | `#4F7CFF` | Primary action, focus, active state |
| Text | `#F5F7FA` | Primary text |
| Muted text | `#9299A8` | Labels and supporting copy |
| Success | `#54C58A` | Video-found status only |

Accent is limited to the logo, send action, focus rings, and selected items. Body
copy should never use the accent color.

### Typography and spacing

- Font: system UI stack initially; Inter may be bundled later if needed.
- Body: 14 px / 1.55.
- Secondary: 12 px / 1.45.
- Eyebrow: 10 px / 1.2, 0.09 em tracking.
- Title: 15 px / 1.35, semibold.
- Spacing follows a 4 px base scale: 4, 8, 12, 16, 20, 24, and 32 px.
- Corners: 8 px controls, 12 px cards, 14 px composer, fully rounded pills.

## States

The conversation region owns six explicit states:

1. `empty` — video available, no messages.
2. `conversation` — one or more completed messages.
3. `loading` — skeleton answer appears after the user message.
4. `no-video` — neutral instruction to open a YouTube video.
5. `error` — inline recoverable error with a retry action.
6. `offline` — persistent muted banner; existing messages remain readable.

Phase 2 only defines these states. Their behavior will be implemented in later
phases.

## Motion and accessibility

- Motion stays between 120 ms and 220 ms with ease-out timing.
- Sidebar entry slides 12 px; messages fade and rise 4 px; button presses scale to
  0.97. Reduced-motion preference disables transforms.
- Every icon-only action requires an accessible name and visible tooltip.
- Focus rings use a 3 px translucent accent outline and must not be removed.
- Text and controls target WCAG AA contrast, with a minimum 40 × 40 px hit area.
- Status changes use a polite live region; loading skeletons are hidden from screen
  readers in favor of a concise `VidMind is responding` label.

## Component boundary

```text
SidebarApp
├── Header
│   └── SettingsMenu
├── VideoContext
└── ConversationPanel
    ├── EmptyState | ChatWindow
    │   └── Message
    │       └── TimestampCard[]
    ├── Loading
    └── ChatInput
```

This boundary keeps video detection, message state, and presentation separate.
The visual components accept data and callbacks; they do not call extension or
backend APIs directly.
