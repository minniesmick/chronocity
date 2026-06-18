<a id="top"></a>

<div align="right">

🇹🇷 [Türkçe](./README_Tr.md)

</div>

<div align="center">

# ChronoCity

**Travel through 5 cities across 226 years of urban history — in real time, in 3D.**

![Version](https://img.shields.io/badge/version-0.1.0-f59e0b?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Web-3b82f6?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20deck.gl%20%2B%20Three.js-8b5cf6?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-e0aaff?style=flat-square)
![Node](https://img.shields.io/badge/node-18%2B-10b981?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-ef4444?style=flat-square)

> ChronoCity renders the architectural evolution of Istanbul, New York, Chicago, Berlin, and Vienna as a live 3D experience. Drag a timeline from 1800 to 2026 and watch buildings rise in real time — height, color, and ambient audio morph together through a single `t` parameter. Built as a CS graduation project (SDP1 + SDP2).

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development](#development)
- [Build & Package](#build--package)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

---

## Overview

ChronoCity is a browser-based 3D urban time-travel experience. It renders real building footprints and heights from open geodata, gates each building by its construction year, and morphs the entire skyline as the user scrubs through time. Every sensory layer — 3D geometry, ambient music, particle overlays — is driven by a single normalized `t` value (0.0 = 1800, 1.0 = 2026), making the system trivially extensible to new cities or data sources.

The project spans two academic semesters: SDP1 builds the visualization engine, SDP2 adds a computational analytics layer (shadow analysis, multi-criteria routing, spatial ML, NL query agent).

---

## Features

### 3D City Engine
- Extruded building geometry from real GeoJSON footprints (NYC: 6,550 buildings, Midtown/Flatiron)
- `construction_year` gate — each building appears only when the active year reaches its build date
- GPU-accelerated transitions (elevation + color, 400 ms) via deck.gl
- Cinematic camera defaults: pitch 50°, bearing −20°, zoom 14.5, maxPitch 75°

### Time Morphing
- Single `t` parameter (0.0–1.0) maps linearly to years 1800–2026
- All layers (geometry, lighting, audio, particles) stay in sync
- Scrub forward/backward — buildings rise and vanish in real time
- Timeline auto-play mode (isPlaying state)

### Day / Night Mode
- Warm daylight: AmbientLight 1.1 + DirectionalLight 1.4 (soft yellow)
- Cool night: AmbientLight 0.5 + DirectionalLight 0.7 (blue-white)
- 800 ms CSS background transition synced to deck.gl lighting swap
- Building color ramp darkens short buildings in night mode

### Multi-City Architecture
- City registry with `hasBuildingData` flag — cities without data are selectable but render nothing (graceful no-op)
- Lazy GeoJSON fetch per city; cached after first load
- Per-city color identity: Istanbul amber, NYC blue, Chicago purple, Berlin green, Vienna red

### Ambient Audio Engine *(Sprint 4 — planned)*
- Web Audio API + Tone.js crossfade between era MP3s (1960s / 1980s / 2000s / modern)
- Audio continues even when the timeline is paused
- Frequency visualizer ring overlay (AnalyserNode → FFT → Canvas)

### Historical Events *(Sprint 3 — planned)*
- Event markers on the timeline (positive / negative / neutral)
- Tap to open a detail popup; "More" triggers a Gemini streaming report

### SDP2 Analytics Layer *(planned)*
- **Sun/shadow engine** — ray-casting + quadtree spatial index; answers "which rooftop is solar-viable?"
- **Multi-criteria router** — A\*/Dijkstra + Pareto optimization; finds quietest/sunniest walking route
- **Urban growth ML** — spatial ML on construction_year data; predicts densification direction
- **Natural language spatial agent** — "Show pre-1920 buildings above 50 m near the waterfront" → instant query

---

## Screenshots

> Screenshots coming soon — run the app locally to see it in action.

Sprint 1 verified: NYC 2026 full skyline, NYC 1900 sparse skyline, day mode warm lighting, night mode dark amber glow.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend framework | React | 18.3 |
| Build tool | Vite | 5.4 |
| Language | TypeScript | 5.6 |
| 3D map engine | deck.gl | 9.0 |
| 3D globe | Three.js | 0.169 |
| Map tiles | MapLibre GL | 4.7 |
| State management | Zustand | 5.0 |
| Animation (UI) | Framer Motion | 11 |
| Animation (camera) | GSAP | 3.12 |
| Audio engine | Tone.js | 15 |
| Backend | FastAPI | latest |
| Realtime | WebSocket (FastAPI /ws) | — |
| Routing | React Router | 6 |

**Communication:** Frontend (Vite :5173) proxies `/api` and `/ws` to FastAPI (:8000). No basemap API key required for Sprint 1 — deck.gl renders standalone on a dark background.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Node.js | 18+ | LTS recommended |
| npm | 9+ | bundled with Node |
| Python | 3.11+ | for FastAPI backend |
| pip | 23+ | — |
| Git | any | — |

No Google Maps or Mapbox API key is needed to run the 3D city view.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/minniesmick/chronocity.git
cd chronocity

# 2. Install frontend dependencies
npm install

# 3. Start the frontend dev server
npm run dev
# → http://localhost:5173
```

```bash
# 4. (Optional) Start the FastAPI backend (separate terminal)
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

Open [http://localhost:5173](http://localhost:5173), click **New York** (the only city with data), and drag the time scrubber.

---

## Configuration

### Vite proxy (`vite.config.ts`)

```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws':  { target: 'ws://localhost:8000', ws: true }
  }
}
```

### Adding a new city

1. Add a `buildings.geojson` to `public/cities/{city-id}/` with properties `{ height: number, construction_year: number | null, name: string | null }`.
2. Register the city in `src/data/cities.ts` with `hasBuildingData: true`.
3. Pick a CSS color from `src/styles/tokens.css` city variables or add a new one.

### Global state (`src/store/useStore.ts`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `t` | `number` | `1` | Normalized time 0.0–1.0 → year 1800–2026 |
| `activeCity` | `CityId \| null` | `null` | Selected city |
| `era` | `EraId` | `"modern"` | Audio era |
| `isDayMode` | `boolean` | `true` | Day/night lighting |
| `isPlaying` | `boolean` | `false` | Timeline auto-play |
| `activeEvent` | `CityEvent \| null` | `null` | Focused historical event |
| `audioReady` | `boolean` | `false` | Web Audio API unlocked |

### Dev automation

In development, `window.useStore` is exposed for deterministic test scripting:

```javascript
// Jump to NYC 1902 in night mode
window.useStore.setState({ t: 0.045, isDayMode: false })
```

---

## Development

### Port map

| Service | Port | Start command |
|---------|------|---------------|
| Vite frontend | 5173 | `npm run dev` |
| FastAPI backend | 8000 | `uvicorn main:app --reload` |

### Coding conventions

- All colors via CSS variables from `src/styles/tokens.css` — no hardcoded hex
- `transform`/`opacity` for animations — never `width`/`height` (60 fps target)
- `t` is the only clock. Never introduce a separate timer for any sensory layer.
- deck.gl HMR can produce zombie instances. If the map stops rendering after edits, stop and restart the dev server.

### Adding a component

1. Check `src/components/` for duplicates first
2. Follow naming: `PascalCase.tsx` + co-located `kebab-case.css`
3. Reference [`.design/chronocity/TASKS.md`](.design/chronocity/TASKS.md) for the active sprint task
4. Mark the task `[x]` when done

---

## Build & Package

```bash
# 1. Type-check + build frontend
npm run build
# Output: dist/ (~2 MB gzipped assets)

# 2. Preview production build locally
npm run preview
# → http://localhost:4173
```

Backend is not bundled — deploy FastAPI separately (e.g. Railway, Render, or a VPS). The frontend is a static SPA and can be hosted on Vercel, Netlify, or GitHub Pages.

---

## Project Structure

```
chronocity/
├── .design/                    # Design docs and Claude Code skills
│   └── chronocity/
│       ├── DESIGN_BRIEF.md     # Aesthetic direction, component inventory
│       ├── TASKS.md            # Sprint task list (S0–S10 + SDP2)
│       └── SKILL_MAP.md        # When to use which design skill
├── backend/
│   ├── main.py                 # FastAPI: /ws WebSocket + /api/health + CORS
│   └── requirements.txt
├── public/
│   └── cities/
│       └── new-york/
│           ├── buildings.geojson   # 6,550 buildings, height + construction_year
│           ├── events/             # Historical event JSON + cover images
│           └── music/              # Era MP3s (1960s/1980s/2000s/modern)
├── src/
│   ├── components/
│   │   ├── MapCanvas.tsx       # deck.gl 3D core, LightingEffect, GeoJsonLayer
│   │   ├── CityExperience.tsx  # Sprint 1 scene shell
│   │   ├── DayNightToggle.tsx  # Segmented day/night button
│   │   ├── DevTimeScrubber.tsx # Temporary dev scrubber (replaced by TimelineBar S3)
│   │   └── sprint1.css         # Scene + UI token-driven styles
│   ├── data/
│   │   └── cities.ts           # City registry (5 cities, hasBuildingData flag)
│   ├── hooks/
│   │   └── useCityBuildings.ts # Lazy GeoJSON fetch hook
│   ├── lib/
│   │   ├── buildingColors.ts   # Height-based amber/ember color ramp
│   │   └── time.ts             # yearFromT / tFromYear helpers
│   ├── store/
│   │   └── useStore.ts         # Zustand global store
│   ├── styles/
│   │   ├── tokens.css          # All CSS custom properties (colors, spacing, type)
│   │   └── global.css          # Reset + base
│   ├── types.ts                # CityId, EraId, BuildingProperties, CityEvent
│   ├── App.tsx                 # Route: null → city selector, city → CityExperience
│   └── main.tsx
├── .gitattributes
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## Roadmap

- [x] Sprint 0 — Scaffold: React + Vite + TS + Zustand + FastAPI + design tokens
- [x] Sprint 1 — 3D core: deck.gl buildings, time morph (1800–2026), day/night toggle
- [ ] Sprint 2 — Entry flow: Three.js globe selector, intro cinematic, city loading screen, React Router
- [ ] Sprint 3 — Timeline: full-width scrubber bar, event markers, event popups
- [ ] Sprint 4 — Audio: era MP3 crossfade (Web Audio API + Tone.js), frequency visualizer
- [ ] Sprint 5 — Multi-city: lazy data loader + fly-to animation, Istanbul / Chicago / Berlin / Vienna data
- [ ] Sprint 6 — Layers: fluid heatmap (Navier-Stokes particles), layer toggle panel, building popup
- [ ] Sprint 7 — Realtime: WebSocket sound notes (pin + record + broadcast), Gemini report drawer
- [ ] Sprint 8 — Polish: onboarding tooltips, Street View blend, compare mode (split-screen)
- [ ] Sprint 9 — PWA: offline cache, install prompt, mobile layout, tablet responsive
- [ ] Sprint 10 — QA: cross-browser testing, Lighthouse audit, jüri demo script
- [ ] SDP2 — Analytics: sun/shadow engine, multi-criteria router, urban growth ML, NL spatial agent

---

## Contributing

This is an academic graduation project. External contributions are welcome for data, bug reports, and suggestions.

```bash
# 1. Fork and clone
git clone https://github.com/minniesmick/chronocity.git

# 2. Create a feature branch
git checkout -b feature/my-feature

# 3. Make changes, then commit
git commit -m "feat: describe what and why"

# 4. Push and open a PR
git push origin feature/my-feature
```

**Project-specific notes:**
- No hardcoded colors or pixel values — use tokens from `src/styles/tokens.css`
- Test on a Chromium browser first (deck.gl WebGL2 behavior varies across engines)
- If adding a city, include a processed `buildings.geojson` with `height` in metres and `construction_year` as integer

---

## Author

**Alper Yusuf Yaman**
[@minniesmick](https://github.com/minniesmick) on GitHub

---

## License

Licensed under the [MIT License](./LICENSE).

© 2026 Alper Yusuf Yaman. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

---

<div align="center">
  <sub>Cities remember everything. ChronoCity lets you remember with them.</sub>
  <br/><br/>
  <a href="#top">↑ back to top</a>
</div>
