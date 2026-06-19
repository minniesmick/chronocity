# Build Tasks: ChronoCity

Generated from: .design/chronocity/DESIGN_BRIEF.md  
Date: 2026-06-12  
Team: 2 aktif (Alper → teknik, Arkadaş → test/rapor), 2 pasif  
Stack: React 18 + Vite + TypeScript + deck.gl + Three.js + Web Audio API + FastAPI

---

## SPRINT 0 — Foundation (Blocker olmadan hiçbir şey başlamaz)

- [x] **Design Tokens**: `src/styles/tokens.css` oluştur. Renkler: `#0A0A0F` zemin, `#F59E0B` amber, `#E2E8F0` metin, `#1E293B` panel. Space Grotesk heading + Inter body. 4px grid spacing scale. _New._

- [x] **Vite + React + TS Proje Scaffold**: Manuel scaffold (`.design` dolu olduğundan), absolute imports (`@/`). Framer Motion + GSAP + Tone.js + deck.gl + three + react-map-gl + maplibre-gl + zustand + react-router bağımlılıkları kuruldu (490 paket). Zustand store + types + cities registry yazıldı. Dev server 5173'te doğrulandı, render OK. _New._

- [x] **Asset Klasör Yapısı**: `/public/cities/{city}/music/`, `/public/cities/{city}/events/{date}/` yapısı 5 şehir için oluşturuldu. NYC `buildings.geojson` (6550 bina, height+construction_year) `public/cities/new-york/`'a kopyalandı. _Not: İstanbul örnek event JSON'ları ertelendi — veri şehri NYC._ _New._

- [x] **11 Şehir Bina Verisi**: Manus.ai ile 11 şehir için bina GeoJSON indirildi (height %100 hepsi). Merkez bbox'a kırpıldı, `public/cities/{city}/buildings.geojson`'a kopyalandı. NYC/Berlin/Moscow/Paris/Vienna/Chicago/London/Tokyo/Madrid/Barcelona/İstanbul. `hasBuildingData: true` tüm şehirler. `CityId` tipi güncellendi. _New._

- [x] **FastAPI Backend Scaffold**: `backend/main.py` — WebSocket endpoint (`/ws`), CORS ayarı, health check. `requirements.txt`. _New._

---

## SPRINT 1 — Risk First: WebGL & 3D Core

> En riskli parça önce. Shader + deck.gl çalışmazsa her şey anlamını yitirir.

- [x] **MapCanvas — deck.gl Base**: Tam ekran `DeckGL`, standalone (basemap key gerekmez), pitch 50° bearing -20° sinematik, LightingEffect (ambient+directional). Default NYC merkezi. `src/components/MapCanvas.tsx`. _Not: Google Maps/Mapbox basemap sonra opsiyonel — şu an deck.gl tek başına koyu zeminde render._ _New. Depends on: Tokens._

- [x] **BuildingLayer — GeoJSON Extrusion**: `GeoJsonLayer` ile `buildings.geojson` (NYC 6550 bina) yüklü, `extruded`, `getElevation: f => f.properties.height`, amber/ember yükseklik rampası. Lazy fetch hook `useCityBuildings` (verisi yok → no-op). construction_year kapısı: bina ≤ aktif yıl ise yükselir. İki screenshot ile doğrulandı (2026 tam skyline → 1900 seyrek). _Not: NYC verisi kullanıldı (OSM değil — construction_year içeriyor, daha iyi)._ _New._

- [x] **TimeUniform (data-driven)**: `t`→yıl morph çalışıyor — construction_year kapısı + amber yükseklik rampası, deck.gl GPU transitions (getElevation/getFillColor 400ms) ile pürüzsüz. `useStore` `t` tüm sisteme yayılır. _Karar: el-yazımı GLSL uTime yerine data-driven + GPU transition (sağlam, aynı görsel). Gerçek GLSL injection opsiyonel hardening olarak ertelendi._ _New._

- [x] **Era Renk Sistemi + Pulse Animasyon**: `colorByEra(year)` — 7 dönem bandı (taş/barok 1870 öncesi → cam-mavi 2010+). Tarihi belirsiz binalar `colorUndated(frame)` — gri-mavi, 20fps RAF loop (~50ms setFrame) ile nefes pulse (opacity 55–95). Dated binalar zamanı gelince dönem rengiyle çıkar, undated her zaman görünür. `buildingColors.ts` tamamen yeniden yazıldı, `MapCanvas.tsx` RAF loop eklendi. _New._

- [x] **DayNightToggle**: Yapışık ikili segmented buton (Gündüz/Gece) üst barda. `isDayMode` store → MapCanvas LightingEffect (gündüz sıcak/parlak ↔ gece loş/soğuk) + bina paleti (gece kısa binalar kararır) + arka plan 800ms CSS geçişi. İki screenshot doğrulandı. `DayNightToggle.tsx`. _New._

---

## SPRINT 2 — Globe & Entry Flow

- [x] **GlobeSelector — Three.js Globe**: `THREE.SphereGeometry(2,64,64)` + PhongMaterial + wireframe atmosfer. 11 şehir noktası (globe child → onunla döner), her biri şehre özel renk. Hover → dot scale lerp 1.7×, label border glow. Raycaster click → `/city/:id` navigate. `ResizeObserver` + auto-rotate 0.0008 rad/frame. _New._

- [x] **Bayrak & Şehir Label**: HTML overlay katmanı — bayrak emoji + şehir adı. RAF döngüsünde `getWorldPosition` → `project(camera)` → CSS transform güncelleme (React state yok, sıfır re-render). Ön yüz kontrolü (camDir dot test). Hover data-attribute → border + name rengi city color. _New. Depends on: GlobeSelector._

- [x] **IntroScene**: Gradient placeholder (TODO: `<video>` arka plan). Logo Framer Motion fade-in (delay stagger). "KEŞFET →" CTA → `/globe`. Exit animasyonu. _New. Video slot hazır, asset bekliyor._

- [x] **CityLoadingScreen**: Overlay mimari (MapCanvas arka planda mount edilir, canvas tam boyuta ulaşır). Flag + şehir adı + ülke + nüfus/kuruluş + 3 milestone typewriter (600ms stagger). setInterval progress bar (1.8s). `AnimatePresence` exit. TODO: `<video>` slot hazır. _New. Depends on: Asset Klasör Yapısı._

React Router v6 bağlandı: `/` → IntroScene, `/globe` → GlobeSelector, `/city/:id` → CityExperience. `AnimatePresence mode="wait"` + `location` key ile route exit animasyonları.

---

## SPRINT 3 — Timeline & Events

- [x] **TimelineBar**: Glassmorphism panel alt-merkez, 820px max genişlik. Büyük mono yıl göstergesi + ▶/⏸ play butonu. `--pct` CSS var ile canlı track rengi. Era tick işaretleri (1800/1870/1918/1945/1980/2000/2010/2026) — aktifler amber. Keyboard: ←/→ = 1 yıl, Shift+←/→ = 10 yıl, Space = play/pause. Auto-play: setInterval 180ms/yıl (~40s tam yolculuk), t=1'de otomatik dur. `t` → Zustand `setT`. _New. DevTimeScrubber yerini aldı._

- [x] **YearIndicator + RadioButton**: Yıl TimelineBar sol tarafında büyük mono gösterge. Era pill radio'ları TimelineBar sağında (60'lar / 80'ler / 2000'ler / Modern). t scrub / auto-play → `eraFromYear()` auto-sync. Manuel click override. `era` → Zustand `setEra`. Müzik klasörleri hazır: `/public/cities/{cityId}/music/{eraId}.mp3` — 11 şehir × 4 era = 44 placeholder oluşturuldu. _New. Depends on: TimelineBar._

- [x] **EventMarker**: Timeline track üstünde 8px renkli noktalar. `positive` yeşil / `negative` kırmızı / `neutral` amber. Uzaklık: >20 yıl gizli, 10-20 yıl %40, <10 yıl tam görünür. ±2 yıl içinde CSS pulse animasyon. Hover → `setActiveEvent` (EventPopup için). `useCityEvents` hook: store `activeCity` → `/public/cities/{city}/events/info.json` fetch. Berlin (9 olay) + İstanbul (9 olay) sample data eklendi. _New. Depends on: TimelineBar._

- [x] **EventPopup**: EventMarker tıklanınca slide-up glassmorphism kart. Badge + yıl + başlık + shortDesc + "Daha fazla" (wikiSlug→TR Wikipedia). ESC / X / dışarı tıkla ile kapat. FM animate prop (AnimatePresence yerine — Strict Mode fix). _New. Depends on: EventMarker._

- [x] **ReplayButton**: Floating 40px amber buton bottom-right. setT(0) + setPlaying(true) + RefreshIcon animate. _New._

---

## SPRINT 4 — Audio Engine

- [x] **EraAudioEngine**: Web Audio API native (Tone.js yok). Module singleton AudioContext. `audioReady` lazy init (ilk click/keydown, autoplay policy). Çift GainNode A/B crossfade 1.5s linearRamp. activeCity+era → `/cities/{city}/music/{era}.mp3` fetch+decodeAudioData. Race condition koruması (loadedKey ref). loop=true. Şehir çıkınca fade-out. 404 sessiz. `src/lib/audioContext.ts` + `src/hooks/useEraAudio.ts`. _New. Depends on: TimelineBar, /public/cities/{city}/music/._

- [x] **FrequencyVisualizer**: `AnalyserNode` (fftSize=128, 64 bin) → Canvas 2D, 32 bar × (3+2)px. requestAnimationFrame getByteFrequencyData. Amber linear gradient per bar (transparan→tam). mix-blend-mode:screen, opacity:0.7. audioReady=false → null (gizli). bottom:116px left, müzik gelince canlı. `src/components/FrequencyVisualizer.tsx`. _New. Depends on: EraAudioEngine._

---

## SPRINT 5 — City Data & Multi-City

- [ ] **CityDataLoader**: Her şehir için GeoJSON lazy load + cache. Şehir değişince `BuildingLayer` swap. Loading state + error boundary. _New. Depends on: MapCanvas, BuildingLayer._

- [ ] **FlyTo Animasyonu**: Şehir seçilince `deck.gl FlyToInterpolator` ile smooth kamera geçişi. Globe → harita zoom-in. _New. Depends on: GlobeSelector, MapCanvas._

- [ ] **Multi-City Event Data**: 5 şehir × 30–50 olay. Wikidata SPARQL sorgusu ile çek, JSON düzenle. Her şehir için `/public/cities/{city}/events/` doldur. _Arkadaşın görevi — veri toplama._

---

## SPRINT 6 — Fluid Heatmap & Layers

- [ ] **FluidHeatmap — Navier-Stokes Particle**: Canvas 2D veya WebGL particle sistemi. IBB/OpenData API'den nüfus/trafik verisi density'ye dönüştürür. `animate-in` opacity + scale. _New. Depends on: MapCanvas._

- [ ] **LayerPanel**: Sağ kenar toggle paneli. Katmanlar: Trafik, Nüfus, Gürültü, Tarihi Fotoğraflar. Her toggle → FluidHeatmap veri kaynağı değişir. _New._

- [ ] **BuildingPopup**: Binaya tıklanınca: bina adı, yükseklik, inşa yılı (GeoJSON properties'den), dönem notu. Glassmorphism card. _New. Depends on: BuildingLayer._

---

## SPRINT 7 — Realtime & AI

- [ ] **WebSocket — Ses Notu**: FastAPI `/ws` endpoint. Haritada uzun basınca pin düşer, mikrofon izni, kayıt → broadcast. Diğer kullanıcılar hover'da duyar. _New. Depends on: FastAPI Backend._

- [ ] **SoundNotePin**: Pin component — animasyonla düşme, hover → ses oynatma, WebSocket event'e subscribe. _New. Depends on: WebSocket._

- [ ] **GeminiReportDrawer**: Opsiyonel. EventPopup "Daha fazla" veya bölge seçimi → slide-in drawer. Gemini API streaming response → satır satır render. _New. Depends on: EventPopup._

---

## SPRINT 8 — Onboarding & Polish

- [ ] **OnboardingPopups**: İlk girişte scroll-triggered tooltip popup'ları (max 4 adım): Timeline kullan, Şehir seç, Olaya tıkla, Ses notu bırak. LocalStorage'da "görüldü" flag. _New._

- [ ] **StreetViewBlend**: Google Street View Panorama embed + CSS `mix-blend-mode` shader overlay. Bina popup'tan tetiklenir. _New._

- [ ] **CompareMode**: Split-screen. Sol/sağ bağımsız `DeckGL` instance. İki şehir veya iki dönem. Sync veya bağımsız timeline. _New. Son sprint — risk düşük ama iş çok._

---

## SPRINT 9 — PWA & Responsive

- [ ] **PWAShell**: `vite-plugin-pwa` konfigürasyonu. Service worker, offline cache (static assets + son kullanılan şehir verisi). Install prompt. _New._

- [ ] **Tablet Responsive (768–1279px)**: LayerPanel collapsed → hamburger. TimelineBar bottom bar'a taşır. _Modify: tüm layout componentları._

- [ ] **Mobile PWA (<768px)**: Sadece harita + TimelineBar + CitySelector. 3D extrusion LOD düşür (height threshold). Ses çalışır. _Modify._

- [ ] **Accessibility Pass**: Kontrast 4.5:1 audit (amber on dark). TimelineBar keyboard nav (←/→, 5% adım). Tüm ikonlar `aria-label`. `prefers-reduced-motion` → shader morph off. _Tüm componentlar._

---

## SDP2 — Analitik Motor (CS Bitirme Derinliği)

> SDP1 temeli: 3D görselleştirme + zaman motoru. SDP2: üstüne analitik beyin eklenir — şehir artık karar veriyor, sadece göstermiyor. Jüri "ee ne işimize yaradı?" diyemez.

- [ ] **Güneş/Gölge Analiz Motoru**: Bina yükseklikleri mevcut (construction_year + height) → ray-casting + polygon-ışın kesişim + quadtree spatial index. Sorular: "Hangi çatı güneş paneline uygun?", "Bu daire sabah güneşi alır mı?". deck.gl SunLight entegrasyonu + GPU compute. _Hesaplamalı geometri. Depends on: BuildingLayer._

- [ ] **Çok-Amaçlı Rota Motoru**: OSM road network'ten graf kur → A*/Dijkstra + Pareto çok-kriterli optimizasyon. Kriterler: mesafe, gürültü skoru, güneş maruziyeti, yeşil alan. Rota 3D sahneye PathLayer ile çizilir. _Graf algoritmaları + Pareto optimizasyon. Novel hedef: klasik mesafe değil konfor/kalite metrikleri. Depends on: MapCanvas._

- [ ] **Kentsel Büyüme ML Modeli**: `construction_year` etiketli 6.550 NYC binası → time-series + spatial ML → "şehir nereye doğru yoğunlaşacak?". Bina-komşuluk grafında GNN ile büyüme tahmini. Heatmap overlay ile görselleştir. _ML + spatial analysis. Depends on: BuildingLayer, FluidHeatmap._

- [ ] **Doğal Dil Mekânsal Sorgu Ajanı**: "Su kenarında 1920 öncesi 50m+ binaları göster" → anlık spatial sorgu + haritada highlight. PostGIS veya yerleşik spatial index + LLM tool-use + RAG + ajan pipeline. Tüm veri ve sahneyi birleştiren konuşma arayüzü. _LLM ajan + mekânsal DB. Depends on: BuildingLayer, EventMarker._

- [ ] **Canlı Trafik/Kalabalık Simülasyonu** _(stretch goal)_: Agent-based model veya sayısal simülasyon (Navier-Stokes türevi) + GPU compute shader. Canlı API verisiyle kalibrasyon. "30 dk sonra burası tıkanır mı?" sorusunu cevaplar. Teknik tavan en yüksek SDP2 maddesi. _Sayısal simülasyon + GPU compute. Depends on: FluidHeatmap._

---

## SPRINT 10 — Test & Dokümantasyon (Arkadaş Sprint'i)

- [ ] **Test Planı**: Her component için manuel test senaryoları. Chrome/Firefox/Edge cross-browser. Performans: 60fps shader hedefi, Lighthouse skoru. _Arkadaş._

- [ ] **Bug Report Şablonu**: GitHub Issues template. Severity, steps to reproduce, ekran görüntüsü. _Arkadaş._

- [ ] **Teknik Rapor Taslağı**: Mimari diyagram, veri kaynakları, API entegrasyonları, shader açıklaması. Bitirme raporu için. _Arkadaş + Alper review._

- [ ] **Jüri Demo Scripti**: 5 dakikalık demo akışı: Intro → Globe → İstanbul seç → Timeline çal → Olaya tıkla → Gece modu → Gemini rapor. _İkisi birlikte._

- [ ] **Design Review**: `/design-review` skill ile brief'e karşı son kontrol. _Alper._

---

## Kritik Path (Sıra Şaşmaz)

```
[SDP1 — devam ediyor]
Tokens → Scaffold → MapCanvas → BuildingLayer → TimeUniform  ✅ S0+S1 tamam
    ↓
GlobeSelector → IntroScene → CityLoadingScreen               ← SPRINT 2 (şu an burada)
    ↓
TimelineBar → EventMarker → EventPopup
    ↓
EraAudioEngine → FrequencyVisualizer
    ↓
CityDataLoader → FlyTo → Multi-City Data
    ↓
FluidHeatmap → LayerPanel
    ↓
WebSocket → GeminiReportDrawer
    ↓
PWA → Responsive → Accessibility → Test

[SDP2 — SDP1 üstüne, bağımsız analitik katman]
BuildingLayer (mevcut veri) → SunShadowEngine
BuildingLayer + OSM Graf    → MultiCriteriaRouter
BuildingLayer (construction_year) → UrbanGrowthML
Tüm veri + LLM              → NLSpatialAgent
FluidHeatmap temel           → TrafficSimulation (stretch)
```

## Görev Dağılımı Özeti

| Sprint | Alper | Arkadaş |
|--------|-------|---------|
| S0 ✅ | Scaffold + Tokens + FastAPI | Asset klasörü + ilk event JSON'ları |
| S1 ✅ | MapCanvas + Shader (kritik) | Berlin/Vienna manuel veri indirme |
| S2 ✅ | Globe + Intro + Loading | Wikidata event veri çekimi |
| S3 ✅ | Timeline + Events + EventPopup + ReplayButton | Event JSON doldurma (30–50 / şehir) |
| S4 ✅ | EraAudioEngine + FrequencyVisualizer | MP3 test + browser ses testi |
| S5 | Multi-city data loader | NYC/Chicago GeoJSON temizleme |
| S6 | Fluid Heatmap + Layers | IBB API endpoint testi |
| S7 | WebSocket + Gemini | API response test senaryoları |
| S8 | Onboarding + StreetView | UX test: ilk kullanıcı deneyimi |
| S9 | PWA + Responsive | Cross-browser + mobile test |
| S10 | Design review + demo | Teknik rapor + bug report |
| **SDP2** | **Güneş/Gölge + Router + ML + NL Ajan** | **SDP2 test senaryoları + teknik rapor bölümü** |

> **Durum özeti (2026-06-19):** SDP1 S0+S1+S2+S3+S4 tamamlandı. 11 şehir verisi, era renk sistemi, pulse animasyon, Three.js globe (UV-aligned lat/lon + drag-rotate + atmosphere rim + earth-night.jpg texture), React Router + AnimatePresence, IntroScene, CityLoadingScreen, TimelineBar (keyboard + auto-play + era pill), EventMarker (click-based, proximity fade, pulse, useCityEvents), EventPopup (glassmorphism, FM animate prop, ESC/X/dışarı), ReplayButton (amber floating, RefreshIcon), EraAudioEngine (Web Audio API singleton, A/B crossfade, autoplay-safe), FrequencyVisualizer (AnalyserNode 64-bin, Canvas 2D 32-bar amber, mix-blend-mode screen) ✅. Berlin + İstanbul event verisi (9'ar olay). 31 animated icon entegre. PRODUCT.md + DESIGN.md hazır. Sıradaki: S5 CityDataLoader + FlyTo.
