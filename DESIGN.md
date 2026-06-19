# Design

## Color Palette

Base: `#0a0a0f` near-black — koyu uzay, sahneyi tutar
Surface: `#12121a` elevated, `#1e293b` panel
Primary Accent: `#f59e0b` amber — kalp atışı, zaman çizelgesi, aktif durum
Accent Bright: `#fbbf24` hover/glow
Accent Dim: `#b45309` pasif
Glow: `rgba(245,158,11,0.35)` ışık halesi

Text hierarchy: `#e2e8f0` primary → `#94a3b8` muted → `#64748b` faint

Event colors: positive `#10b981` / negative `#ef4444` / neutral `#f59e0b`

All values via CSS custom properties in `src/styles/tokens.css`. No hardcoded hex in components.

## Typography

Heading + Mono: Space Grotesk (geometric, confident)
Body: Inter (neutral legibility)

Scale: xs(12) → sm(14) → base(16) → lg(20) → xl(28) → 2xl(40) → 3xl(64)
Key moments: `--text-2xl` year indicator, `--text-3xl` intro wordmark
Tracking: `--tracking-wide` (0.08em) mono labels, `--tracking-wider` (0.18em) cinematic caps

## Motion

Easing: `--ease-cinematic: cubic-bezier(0.16,1,0.3,1)` — dominant; confident deceleration
Standard: `cubic-bezier(0.4,0,0.2,1)`
Durations: fast 160ms / base 320ms / slow 800ms

Key rule: entrances ease-out-expo, exits 75% of enter duration.
No bounce. No elastic. No decorative spin.
prefers-reduced-motion: disable all animations.

Signature animations:
- Globe: scale 0.85→1 + opacity 0→1 on mount (600ms ease-cinematic)
- City dots: stagger 40ms each, scale 0→1.2→1
- TimelineBar: slide-up from bottom 24px (400ms ease-cinematic)
- Header: slide-down from -20px (350ms ease-cinematic, 200ms delay)
- Year number: blur 4px→0 + opacity 0→1 on change (120ms ease-out)
- Era pill active: background color transition 200ms
- Loading progress: ease-out width fill
- Route transitions: Framer Motion fade, 400ms

## Components

Panel style: glassmorphism — `rgba(30,41,59,0.72)` + `blur(14px)` + `1px border rgba(226,232,240,0.16)` + `var(--shadow-panel)`
Radius: pill for small controls, lg(14px) for panels
Buttons: amber accent for primary, panel-translucent for secondary

Timeline: full-width bottom-center, 820px max, pill era buttons right side
Globe: full-screen Three.js canvas, HTML label overlay, zero React re-renders in RAF

## Layout

Full-screen canvas base, UI elements absolute positioned on top.
CityExperience: header top-left-right, TimelineBar bottom-center, loading overlay z-50.
GlobeSelector: full-screen canvas + HTML labels.
IntroScene: centered column, gradient bg.

Spacing scale: 4px base grid (space-1 through space-7).
