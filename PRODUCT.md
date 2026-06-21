# Product

## Register

product

## Users

CS graduation jury members (primary evaluators), urban-history enthusiasts, and the developer's own portfolio audience. Context: seated at desktop, evaluating a demo in a darkened presentation setting or exploring casually. Not mobile-first. Task: "understand what the project does within 30 seconds, then freely explore cities across time."

## Product Purpose

ChronoCity renders 170,000+ real building footprints across 11 world cities as a live 3D time-travel experience. A single timeline slider gates buildings by their construction year; the skyline morphs in real time from 1800 to 2026. An XGBoost + PyTorch MLP model predicts the construction era of unlabeled buildings from geometry and urban context. Built as a CS capstone (Bitirme Projesi 1 + 2). Success = jury can understand the technical depth AND feel the cinematic product quality simultaneously.

## Brand Personality

Cinematic. Precise. Reverent.

## Anti-references

- Google Maps / Apple Maps — too utilitarian, too bright, no narrative
- Tourist-city apps — kitschy, oversaturated, no data depth
- Generic data dashboards — cold, grid-heavy, no atmosphere
- Mapbox demo sites — technically impressive but sterile / performative

## Design Principles

1. **Data as performance** — every metric, number, and color on screen should feel like it's revealing something, not labeling it.
2. **Atmosphere earns trust** — dark, precise, cinematic UI signals that serious work happened underneath. The environment IS the argument.
3. **One thing at a time** — the user scrubs time OR reads a popup OR reads a building hover. Never competing for the same moment.
4. **Controls disappear into the experience** — HUD elements (timeline, era legend, day/night toggle) are always accessible but never dominant. The 3D view IS the product.
5. **Transfer cross-city teaches** — the geographic breadth (11 cities, not 1) is the academic contribution. UI must support rapid city switching without breaking immersion.

## Accessibility & Inclusion

No WCAG level specified; baseline contrast for legibility. Keyboard navigation not currently targeted (3D camera is mouse/touch). `prefers-reduced-motion` not yet implemented — flagged for post-demo polish.
