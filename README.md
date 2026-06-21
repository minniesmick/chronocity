<a id="top"></a>

<div align="right">

🇹🇷 [Türkçe](./README_Tr.md)

</div>

<div align="center">

# ChronoCity

**Travel through 11 cities across 226 years of urban history — in real time, in 3D.**

![Version](https://img.shields.io/badge/version-0.2.0-f59e0b?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Web-3b82f6?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%2019%20%2B%20deck.gl%20%2B%20FastAPI-8b5cf6?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-e0aaff?style=flat-square)
![Node](https://img.shields.io/badge/node-18%2B-10b981?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-ef4444?style=flat-square)

> ChronoCity renders the architectural evolution of 11 world cities as a live 3D experience. Drag a timeline from 1800 to 2026 — buildings rise in real time, era-matched music plays, and an XGBoost/MLP model predicts the construction era of every building from its geometry and urban context. Built as a CS graduation project (Bitirme Projesi 1 + 2).

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [ML Capstone](#ml-capstone)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [ML Setup](#ml-setup)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Overview

ChronoCity is a browser-based 3D urban time-travel experience. It renders real building footprints and heights from open geodata, gates each building by its construction year, and morphs the entire skyline as the user scrubs through time. Every sensory layer — 3D geometry, ambient music, particle overlays — is driven by a single normalized `t` value (0.0 = 1800, 1.0 = 2026).

The project has two tracks:

- **SDP1 (S0–S5)** — 3D visualization engine: globe selector, timeline, audio, multi-city
- **Capstone ML** — Era prediction: 43,500 labeled buildings across 11 cities, XGBoost + PyTorch MLP, FastAPI inference endpoints

---

## Features

### 3D City Engine
- Extruded building geometry from real GeoJSON footprints — **170,000+ buildings** across 11 cities
- `construction_year` gate: each building appears only when the active year reaches its build date
- GPU-accelerated transitions (elevation + color, 400 ms) via deck.gl
- Cinematic camera defaults: pitch 50°, bearing −20°, zoom 14.5

### Time Morphing
- Single `t` parameter (0.0–1.0) maps linearly to years 1800–2026
- Keyboard: `←/→` = 1 year, `Shift+←/→` = 10 years, `Space` = play/pause
- Auto-play at 180 ms/year (~40 s full journey)

### 7 Era Color System
| Era | Period | Color |
|-----|--------|-------|
| Taş/Barok | < 1870 | Brown |
| Gründerzeit | 1870–1918 | Tan |
| Art Deco | 1918–1945 | Gold |
| Brutalizm | 1945–1965 | Slate |
| Prefab | 1965–1980 | Peru |
| Cam & Çelik | 1980–2000 | Steel Blue |
| Modern | ≥ 2000 | Green |

### Day / Night Mode
- Warm daylight ↔ cool night with 800 ms CSS transition
- Three.js globe swaps earth texture; deck.gl lighting synced

### Multi-City
- 11 cities: New York, Paris, Vienna, Chicago, Berlin, Moscow, London, Barcelona, Madrid, Tokyo, Istanbul
- Lazy GeoJSON fetch per city; module-level cache (no re-fetch)
- Per-city color identity and globe card

### Audio Engine
- Web Audio API native crossfade between era MP3s (1.5 s linearRamp)
- Frequency visualizer: AnalyserNode (fftSize=128) → Canvas 32-bar spectrum

### Historical Events
- Event markers on timeline (positive / negative / neutral)
- Click → glassmorphism popup with Wikipedia link

---

## ML Capstone

> Research question: *Can building construction era be predicted from geometric footprint features and urban context?*

### Data (ML-1)

**43,500 labeled buildings** from 6 open data sources:

| Source | City | Buildings | Coverage |
|--------|------|-----------|----------|
| NYC PLUTO | New York | 6,453 | 98% |
| ADEME DPE | Paris | 13,334 | 97% |
| Wien Bauperiode WFS | Vienna | 13,872 | 76% |
| Chicago Building Permits API | Chicago | 4,275 | 94% |
| Berlin Geoportal | Berlin | 2,949 | 10% |
| OSM start_date + Overpass | All cities | ~2,700 | partial |

GHSL (Global Human Settlement Layer, JRC) — 5 epochs 1975–2020, 55 GeoTIFF tiles downloaded — used as `ghsl_neighborhood_year` **input feature** (neighborhood urbanization epoch), not as a construction-year label.

### Features (ML-2)

14 features per building:

| Feature | Description |
|---------|-------------|
| `area_m2`, `perimeter_m` | Footprint size (Web Mercator) |
| `compactness` | 4π·area/perimeter² |
| `aspect_ratio` | Bounding box elongation |
| `n_vertices` | Shape complexity |
| `height` | Building height in metres |
| `dist_to_center_km` | Haversine from city center |
| `ghsl_neighborhood_year` | GHSL first-urbanization epoch |
| `neighbor_mean_height` | Mean height of 50 nearest neighbors |
| `building_density_200m` | Building count within 200 m radius |
| `lat`, `lon` | Centroid coordinates |

### Results

| Model | Within-city CV F1 | Cross-city F1 |
|-------|------------------|--------------|
| XGBoost (n=500, depth=6) | **0.561** ± 0.009 | 0.057 |
| PyTorch MLP (4-layer, CUDA) | 0.469 | 0.089 |

**Key findings:**
- Geographic coordinates account for **58% of feature importance** — within-city signal is strong but non-transferable
- Footprint shape features (compactness, aspect ratio, n_vertices, area) have **zero importance** — shape does not encode era
- Real signal: **height + neighbor height + building density** (urban morphology)
- Cross-city transfer fails without domain adaptation — documented as the academic contribution

### Inference API (ML-3)

See [API Reference](#api-reference) below.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend framework | React | 19 |
| Build tool | Vite | 5.4 |
| Language | TypeScript | 5.6 |
| 3D map engine | deck.gl | 9.0 |
| 3D globe | Three.js | 0.169 |
| Map tiles | MapLibre GL | 4.7 |
| State management | Zustand | 5.0 |
| Animation | Framer Motion | 11 |
| Backend | FastAPI | 0.138 |
| ML | XGBoost 3.2 + PyTorch 2.12 (CUDA) | — |
| Spatial | GeoPandas, pyproj, scikit-learn | — |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/minniesmick/chronocity.git
cd chronocity

# 2. Frontend
npm install
npm run dev
# → http://localhost:5173

# 3. Backend (separate terminal)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

> The ML model (`era_model.pkl`) is not committed to git (large binary).  
> Run `python ml/train_model.py --model xgb` to generate it. See [ML Setup](#ml-setup).

---

## ML Setup

Requires the enriched `buildings.geojson` files (already in repo) and GHSL rasters (separately downloaded to `D:/PROJELER/ghsl_raw/`).

```bash
cd backend

# 1. Feature engineering — extracts 14 features, computes KNN neighborhood stats
#    Output: D:/PROJELER/ml_data/{train,test_gt,predict,features_all}.parquet
python ml/feature_engineering.py

# 2. Train XGBoost + PyTorch MLP
python ml/train_model.py --model both
# Output: backend/era_model.pkl, era_model_xgb.json, era_model_mlp.pt

# 3. Start API
uvicorn main:app --port 8000
```

---

## API Reference

### `GET /api/health`
```json
{ "status": "ok", "service": "chronocity" }
```

### `POST /api/predict-era`
Predict era for a single building.

```json
// Request
{
  "city": "vienna",
  "lon": 16.370, "lat": 48.208,
  "height": 18.0,
  "area_m2": 600, "building_density_200m": 15
}

// Response
{
  "era": 1,
  "era_name": "Gründerzeit",
  "era_period": "1870–1918",
  "era_color": "#C19A6B",
  "confidence": 0.590,
  "probabilities": { "Taş/Barok": 0.189, "Gründerzeit": 0.590, ... }
}
```

### `POST /api/predict-era/batch`
Batch predict up to 1000 buildings.

```json
// Request
{ "city": "paris", "buildings": [{ ...BuildingFeatures }, ...] }
```

### `GET /api/predict-city/{city}?limit=5000`
Predict all unlabeled buildings for a city from `predict.parquet`.

```json
// Response
{
  "city": "tokyo",
  "count": 200,
  "era_distribution": { "Gründerzeit": 186, "Brutalizm": 8, "Prefab": 6 },
  "buildings": [{ "lon": ..., "lat": ..., "predicted_era_name": "Gründerzeit", "confidence": 0.65 }, ...]
}
```

---

## Project Structure

```
chronocity/
├── .design/
│   └── chronocity/
│       ├── DESIGN_BRIEF.md
│       ├── TASKS.md              # Sprint + ML task list (updated)
│       └── SKILL_MAP.md
├── backend/
│   ├── main.py                   # FastAPI: health + predict-era + predict-city + /ws
│   ├── predict_era.py            # Model loading + inference helpers
│   ├── requirements.txt
│   ├── era_model.pkl             # (gitignored — regenerate with train_model.py)
│   └── ml/
│       ├── enrich_buildings.py   # ML-1: PLUTO, DPE, Wien, Chicago, OSM, GHSL enrichment
│       ├── feature_engineering.py # ML-2: 14 features, BallTree KNN, parquet output
│       ├── train_model.py        # ML-2: XGBoost + PyTorch MLP training
│       ├── experiment_geom_only.py # Ablation: pure morphology without lat/lon
│       ├── find_ghsl_tiles.py    # GHSL tile calculator (Mollweide projection)
│       └── download_ghsl.py      # GHSL batch downloader (5 epochs × 11 tiles)
├── public/
│   └── cities/
│       └── {city}/
│           ├── buildings.geojson  # Enriched: height + construction_year + data_source + ghsl_neighborhood_year
│           ├── events/info.json
│           └── music/{era}.mp3
├── src/
│   ├── components/
│   │   ├── MapCanvas.tsx
│   │   ├── GlobeSelector.tsx
│   │   ├── TimelineBar.tsx
│   │   ├── EventMarker.tsx
│   │   ├── EventPopup.tsx
│   │   ├── BuildingPopup.tsx
│   │   ├── EraAudioEngine.tsx (hook)
│   │   └── FrequencyVisualizer.tsx
│   ├── lib/
│   │   ├── buildingColors.ts     # Era color system (7 bands)
│   │   ├── eraColors.ts
│   │   └── audioContext.ts
│   ├── store/useStore.ts
│   └── types.ts
├── .gitignore
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## Roadmap

- [x] S0 — Scaffold: React 19 + Vite + TS + Zustand + FastAPI + design tokens
- [x] S1 — 3D core: deck.gl buildings, time morph (1800–2026), day/night toggle, era colors
- [x] S2 — Globe: Three.js globe selector, intro cinematic, city loading screen, React Router
- [x] S3 — Timeline: scrubber bar, event markers, event popups, replay button
- [x] S4 — Audio: era MP3 crossfade (Web Audio API), frequency visualizer
- [x] S5 — Multi-city: 11 cities, lazy data loader, fly-to animation, building popup
- [x] ML-1 — Data: 43,500 labeled buildings, 6 open data sources, GHSL neighborhood feature
- [x] ML-2 — Model: XGBoost (CV F1=0.561) + PyTorch MLP (CUDA), cross-city evaluation
- [x] ML-3 — API: `/api/predict-era`, `/api/predict-era/batch`, `/api/predict-city/{city}`
- [ ] ML-4 — Frontend: provenance badges (PLUTO/OSM/AI), AI predicted building visuals, filter panel
- [ ] NLP — Ollama Llama 3.1 8B + RAG (ChromaDB) + function calling + Chat UI
- [ ] S10 — QA: cross-browser, Lighthouse, jüri demo script, technical report

---

## Author

**Alper Yusuf Yaman**
[@minniesmick](https://github.com/minniesmick) on GitHub

---

## License

Licensed under the [MIT License](./LICENSE).

© 2026 Alper Yusuf Yaman.

---

<div align="center">
  <sub>Cities remember everything. ChronoCity lets you remember with them.</sub>
  <br/><br/>
  <a href="#top">↑ back to top</a>
</div>
