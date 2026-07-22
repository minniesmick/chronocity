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

- [x] **GlobeSelector — Three.js Globe**: `THREE.SphereGeometry(2,64,64)` + PhongMaterial. 11 şehir noktası. UV-aligned `latLonToVec3` formülü. Drag-to-rotate + autoPause 90 frame. Raycaster click. Auto-rotate 0.0008 rad/frame. **Gündüz/gece texture swap**: `earth-night.jpg` ↔ `earth-day.jpg` — `isDayMode` store ile anlık geçiş + ışık intensity/renk güncelleme (textureCacheRef, ambientRef, sunRef, atmMatRef). Varsayılan: gece. _New._

- [x] **Bayrak & Şehir Label → Lüks Kart**: `.globe-city-card` glassmorphism — left border (şehre özel renk), bayrak emoji (16px), şehir adı uppercase+tracking, ülke adı (city-color). Downward triangle pointer (CSS ::after). Hover glow (color-mix). DayNightToggle sağ üst overlay. RAF döngüsünde `getWorldPosition → project(camera)` → CSS transform (sıfır React re-render). _New. Depends on: GlobeSelector._

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

> **Not (2026-07-22):** MP3 asset'leri hiç eklenmedi — motor çalışıyor ama içerik yok. Kırık izlenim vermemek için era pill'leri + FrequencyVisualizer + useEraAudio `FEATURES.music=false` bayrağıyla gizlendi (`src/config.ts`). Müzik dosyaları eklenince bayrak açılır, her şey geri gelir.

---

## SPRINT 5 — City Data & Multi-City

- [x] **CityDataLoader**: `useCityBuildings` → module-level Map cache. İkinci ziyarette re-fetch yok. Yeni şehir yüklenirken eski data tutulur (flash of empty map yok). useState initializer: cache hit → loading:false anında. _New. Depends on: MapCanvas, BuildingLayer._

- [x] **FlyTo Animasyonu**: DeckGL `initialViewState` (uncontrolled) → controlled `viewState + onViewStateChange`. Mount: zoom=5, pitch=20. 300ms sonra `FlyToInterpolator({ speed: 1.4 })` → zoom=14.5, pitch=50, bearing=-20, duration=2200ms. _New. Depends on: GlobeSelector, MapCanvas._

- [x] **BuildingPopup**: Bina tıklanınca lüks glassmorphism kart. 46px mono yükseklik (era rengi). Animated height bar (0→pct). Era label (Gründerzeit/Brutalizm/vb.). Sol border = `--bpop-accent` (era-matched). AnimatePresence key={x-y}. Viewport clamp. DeckGL onClick: bina → open, boş alan → close. `eraColors.ts`'ten renk. _New. Depends on: BuildingLayer._

- [x] **eraColors.ts**: Paylaşımlı era renk modülü. 7 dönem × {hex, label, yearStart, yearEnd}. `eraByYear(year)` → EraColor. `ERA_ID_COLORS`: EraId → building era rengi. BuildingPopup + TimelineBar era pills + GlobeSelector senkron. _New._

- [x] **Multi-City Event Data**: Plan değişti — Wikidata SPARQL yerine akademik literatür. 11 şehrin tamamı akademik İngilizce olaylarla dolduruldu (8–22 olay/şehir), APA in-text citation + şehir başına `events/references.md` bibliyografyası. Wikipedia referans olarak kullanılmadı; `wikiSlug` yalnız UI "Daha fazla" linki için. _(2026-07: NY/Paris/Vienna/Chicago/London/Barcelona/Madrid/Moscow/Tokyo; 2026-07-22: Berlin + İstanbul TR→EN çevrildi — 11/11 aynı format.)_

---

## ARA SPRINT (2026-06-22 → 2026-07-22) — v0.3 Görsel Cila + Performans

> Planlanmamış ama gerçekleşen iş. UX_advice.md + Fable_Advice.md kaynaklı.

- [x] **NASA Texture Upgrade**: Globe gece 8K Black Marble (7.7MB) + gündüz Blue Marble (2.4MB). Progressive yükleme: önce `earth-night-2048.jpg` (0.6MB) anında, 8K arkada inince swap.
- [x] **Galaxy Intro + Starfield**: Kamera z 30→18 ease-out zoom (1.75s), 1800 yıldız + 380 mavi Samanyolu bandı noktası (`THREE.Points`).
- [x] **UX_advice 1A–1G**: Connector dash-flow animasyonu, atmosfer rim 0.20/0.10, mouse parallax (sentinel-guard'lı), city card `scale(0.94→1)` entrance, FLY TO hover glow (color-mix), fly-to kamera animasyonu (24-frame lerp → navigate, reduced-motion'da direkt navigate).
- [x] **Şehir Ekranı Cilası**: Gece modu bina wireframe, satellite opacity 0.45/0.28, map-vignette, `city-year-bg` dekoratif yıl overlay, BuildingPopup isim 2 satır clamp.
- [x] **Fable Batch 1 — Performans (2026-07-22)**: Bina katmanı dated/undated ikiye bölündü — pulse artık layer opacity uniform'u (170K binanın fill color attribute'u 20fps yeniden hesaplanmıyor; undated yoksa RAF hiç çalışmıyor). Route-level code splitting (`React.lazy`: Three.js yalnız /globe, deck.gl yalnız /city). Font self-host (@fontsource: Space Grotesk + Inter + JetBrains Mono — JetBrains Mono ilk kez gerçekten yükleniyor). Ölü deps çıkarıldı: tone/gsap/maplibre-gl/react-map-gl (−57 paket). `useCityEvents` module cache, zoom store yazımı 0.1 adım guard'lı, GlobeSelector unmount'ta tam scene dispose (GPU leak fix).
- [x] **Deep-link**: `/city/:id?year=1931` — mount'ta okur, `YearUrlSync` debounced replaceState ile yazar. Jüri demo script'i için tek-link yıl atlama.
- [x] **EventPopup**: wiki linkleri `en.wikipedia.org` (içerik akademik İngilizce olduğundan).
- [x] **Sürüm senkronu**: package.json 0.1.0 → 0.3.0 (README badge ile uyumlu).

---

> **⚠️ Vizyon değişikliği (2026-06-21):** Aşağıdaki Sprint 6–9 ESKİ vizyona ait. FluidHeatmap, WebSocket ses notu, StreetViewBlend, CompareMode, PWA **iptal / süresiz ertelendi** — yerini CAPSTONE ML + NLP aldı. Bölümler tarihsel kayıt olarak duruyor.

## SPRINT 6 — Fluid Heatmap & Layers _(ESKİ VİZYON — İPTAL)_

- [ ] **FluidHeatmap — Navier-Stokes Particle**: Canvas 2D veya WebGL particle sistemi. IBB/OpenData API'den nüfus/trafik verisi density'ye dönüştürür. `animate-in` opacity + scale. _New. Depends on: MapCanvas._

- [ ] **LayerPanel**: Sağ kenar toggle paneli. Katmanlar: Trafik, Nüfus, Gürültü, Tarihi Fotoğraflar. Her toggle → FluidHeatmap veri kaynağı değişir. _New._

- [ ] **BuildingPopup**: Binaya tıklanınca: bina adı, yükseklik, inşa yılı (GeoJSON properties'den), dönem notu. Glassmorphism card. _New. Depends on: BuildingLayer._

---

## SPRINT 7 — Realtime & AI _(ESKİ VİZYON — GeminiReportDrawer yerini NLP capstone'a bıraktı)_

- [ ] **WebSocket — Ses Notu**: FastAPI `/ws` endpoint. Haritada uzun basınca pin düşer, mikrofon izni, kayıt → broadcast. Diğer kullanıcılar hover'da duyar. _New. Depends on: FastAPI Backend._

- [ ] **SoundNotePin**: Pin component — animasyonla düşme, hover → ses oynatma, WebSocket event'e subscribe. _New. Depends on: WebSocket._

- [ ] **GeminiReportDrawer**: Opsiyonel. EventPopup "Daha fazla" veya bölge seçimi → slide-in drawer. Gemini API streaming response → satır satır render. _New. Depends on: EventPopup._

---

## SPRINT 8 — Onboarding & Polish _(ESKİ VİZYON — shortcut overlay fiilen yapıldı, kalanı iptal)_

- [ ] **OnboardingPopups**: İlk girişte scroll-triggered tooltip popup'ları (max 4 adım): Timeline kullan, Şehir seç, Olaya tıkla, Ses notu bırak. LocalStorage'da "görüldü" flag. _New._

- [ ] **StreetViewBlend**: Google Street View Panorama embed + CSS `mix-blend-mode` shader overlay. Bina popup'tan tetiklenir. _New._

- [ ] **CompareMode**: Split-screen. Sol/sağ bağımsız `DeckGL` instance. İki şehir veya iki dönem. Sync veya bağımsız timeline. _New. Son sprint — risk düşük ama iş çok._

---

## SPRINT 9 — PWA & Responsive _(ERTELENDİ — demo sonrası)_

- [ ] **PWAShell**: `vite-plugin-pwa` konfigürasyonu. Service worker, offline cache (static assets + son kullanılan şehir verisi). Install prompt. _New._

- [ ] **Tablet Responsive (768–1279px)**: LayerPanel collapsed → hamburger. TimelineBar bottom bar'a taşır. _Modify: tüm layout componentları._

- [ ] **Mobile PWA (<768px)**: Sadece harita + TimelineBar + CitySelector. 3D extrusion LOD düşür (height threshold). Ses çalışır. _Modify._

- [ ] **Accessibility Pass**: Kontrast 4.5:1 audit (amber on dark). TimelineBar keyboard nav (←/→, 5% adım). Tüm ikonlar `aria-label`. `prefers-reduced-motion` → shader morph off. _Tüm componentlar._

---

## CAPSTONE ML — Bina Era Tahmin Sistemi (Bitirme Projesi 1 Çekirdeği)

> **Araştırma sorusu:** Bina geometrik özellikleri (footprint şekli, alan, yükseklik, komşuluk bağlamı, konum) kullanılarak yapım dönemi tahmin edilebilir mi? Eğitim: NY + Berlin. Test: Tokyo, İstanbul, Barcelona. Katkı: çok şehirli açık tarihi bina yaşı veri seti.

### ML-1 — Veri Mühendisliği & Zenginleştirme

- [x] **NYC PLUTO Pipeline**: 6,453 bina %98 etiketli. `data_source: "NYC_PLUTO"`. GeoPandas spatial join tamamlandı.

- [x] **Berlin Geoportal Baujahr**: 2,949 bina %10 etiketli (`data_source: "Berlin_Geoportal"`). _Hedef %40 tutturulamadı — WFS erişim sorunu. Kısmi veri train'e dahil._

- [x] **Paris APUR + Wien Open Data**: Paris DPE (ADEME) 13,334 bina %97 (`data_source: "Paris_DPE"`). Wien Bauperiode WFS 13,872 bina %76 (`data_source: "Wien_OD"`). Chicago permits API 4,275 bina %94 eklendi (`data_source: "Chicago_Permits"`). Toplam: 43,500 etiketli bina.

- [x] **GHSL Entegrasyonu**: JRC GHS_BUILT_S 5 epoch (1975–2020), 55 GeoTIFF indirildi. **Label değil feature** olarak kullanıldı: `ghsl_neighborhood_year` (mahallenin ilk kentleşme dönemi). Tüm 170K bina için sample alındı.

- [x] **`data_source` Alanı**: Tüm binalarda mevcut. Değerler: "NYC_PLUTO" | "Berlin_Geoportal" | "Paris_DPE" | "Wien_OD" | "Chicago_Permits" | "OSM_start_date" | "OSM".

### ML-2 — Feature Engineering & Model Eğitimi

- [x] **Geometrik Feature Çıkarımı**: `area_m2`, `perimeter_m`, `compactness`, `aspect_ratio`, `n_vertices`, `height`, `lat`, `lon`, `dist_to_center_km`. `backend/ml/feature_engineering.py`. 170K bina, 14 feature.

- [x] **Komşuluk Feature'ları**: BallTree ile 50 NN per city. `neighbor_mean_height`, `neighbor_mean_year`, `neighbor_std_year`, `building_density_200m`. **Bulgu:** `neighbor_mean_year` leakage yarattı (test şehirlerde <%3 label → city median), son modelden çıkarıldı.

- [x] **Baseline: XGBoost Era Classifier**: CV F1-macro=**0.561** ± 0.009 (5-fold). Cross-city F1=0.057. Confusion matrix belgelendi. `backend/ml/train_model.py`.

- [x] **PyTorch MLP Comparison**: 4-katmanlı MLP, BatchNorm, Dropout. RTX 3060 Ti CUDA'da eğitildi. Train F1=0.469, Test F1=0.089. XGBoost within-city'de üstün. _SHAP yapılmadı — XGBoost feature_importances_ kullanıldı._

- [x] **Cross-City Evaluation**: Train: NY+Paris+Wien+Chicago+Berlin+Moscow (42,137). Test: London+Tokyo+Barcelona+Madrid+İstanbul (1,387). **Bulgu:** Koordinatlar (%58 önem) within-city iyi ama cross-city transfer engeller. Saf geometri (compactness/aspect/n_verts) = 0 önem. Urban morphology (height+density) gerçek sinyal. `backend/ml/experiment_geom_only.py`.

- [x] **Model Export**: `backend/era_model.pkl` (XGBoost sklearn pipeline) + `era_model_xgb.json` + `era_model_mlp.pt`.

### ML-3 — Backend Inference

- [x] **`POST /api/predict-era`**: Çalışıyor. Output: `{era, era_name, era_period, era_color, confidence, probabilities}`. `backend/predict_era.py` + `backend/main.py`.

- [x] **`POST /api/predict-era/batch`**: Batch (max 1000 bina). Çalışıyor.

- [x] **`GET /api/predict-city/{city}`**: predict.parquet'ten unlabeled binalar → era distribution + ilk 100 tahmin. Çalışıyor.

### ML-4 — Frontend Entegrasyonu

- [ ] **BuildingPopup Provenance Badge**: `data_source`'a göre renkli badge: Altın "NYC PLUTO ✓" / Gümüş "OSM" / Bronz "GHSL" / Mor "AI Tahmini". Kendi işlediğin veriyi kullanıcıya göster.

- [ ] **AI Predicted Binalar Görsel Farkı**: `AI_Predicted` binalar düşük opaklık + nokta desen dokusu veya kenarlık ile gösterilir. Üstüne hover → "AI tahmini: %73 Brutalizm" badge.

- [ ] **Veri Kaynağı Filtre Paneli**: Toggle layer: "Sadece doğrulanmış", "AI tahminleri dahil", "Hepsini göster". LayerPanel veya MapCanvas legend olarak.

- [ ] **Şehir Karşılaştırma Analitik Paneli** _(stretch)_: "Berlin vs NYC: savaş sonrası yeniden yapılanma karşılaştırması" — era dağılım bar chart, iki şehirde ortalama bina yüksekliği dekada göre. Recharts veya D3.

---

## CAPSTONE NLP — AI Şehir Rehberi

> **Mimari:** Llama 3.1 8B local (Ollama) + RAG (bina/event dataset üzerinde) + function calling (uygulama state kontrolü). LLM eğitilmiyor — kullanılıyor. ML katkısı era tahmin modeli; NLP katkısı domain-specific RAG + agent.

- [ ] **Ollama Kurulum + Llama 3.1 8B**: Ollama Docker veya binary kur, `llama3.1:8b` model indir. FastAPI üzerinden `/api/chat` endpoint (Ollama Python client). RTX 3060 Ti'da ~6 token/s.

- [ ] **RAG Pipeline**: Building + event verilerini chunk'la (şehir × era × event). Embedding: `nomic-embed-text` (Ollama, ücretsiz). Vector DB: ChromaDB local. Query: kullanıcı sorusu → top-k retrieval → context + Llama.

- [ ] **Function Definitions**: LLM'in çağırabileceği tool'lar:
  ```json
  set_city(city_id), set_year(year), set_era(era_id),
  highlight_buildings(era_id), show_event(event_id),
  compare_cities(city_a, city_b), filter_by_source(source)
  ```
  FastAPI function call handler → WebSocket/SSE ile frontend'e uygulama komutu gönder.

- [ ] **Chat UI Komponenti**: Sağ kenar açılır panel. Mesaj input + send. Streaming response (SSE). Bot mesajlarında "Şehri değiştiriyorum..." animasyonu + haritada değişim eş zamanlı. _Depends on: Ollama, FastAPI, RAG._

- [ ] **Örnek Guided Tour**: "Bana Berlin'in 1945 sonrası dönüşümünü göster" → bot `set_city("berlin")` → `set_year(1945)` → `highlight_buildings("Brutalizm")` → 3 paragraflık anlatı üretir. Demo için scriptlendi.

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
[SDP1 — TAMAMLANDI ✅]
Tokens → Scaffold → MapCanvas → BuildingLayer → TimeUniform ✅
GlobeSelector → IntroScene → CityLoadingScreen ✅
TimelineBar → EventMarker → EventPopup ✅
EraAudioEngine → FrequencyVisualizer ✅
CityDataLoader → FlyTo → BuildingPopup → eraColors → Globe day/night → Bayraklar ✅

[CAPSTONE ML — Sıradaki]
PLUTO pipeline (GeoPandas spatial join)
    ↓
GHSL entegrasyonu (Tokyo/İstanbul/Barcelona)
    ↓
Feature engineering (footprint geom + komşuluk istatistikleri)
    ↓
XGBoost baseline → PyTorch MLP → Cross-city evaluation
    ↓
FastAPI /predict-era + /predict-city
    ↓
Frontend: AI predicted buildings + data provenance badges

[CAPSTONE NLP — ML ile paralel başlanabilir]
Ollama kurulum + Llama 3.1 8B
    ↓
RAG pipeline (ChromaDB + nomic-embed-text)
    ↓
Function calling definitions + FastAPI handler
    ↓
Chat UI komponenti + SSE streaming
    ↓
Guided tour demo scripti
```

## Görev Dağılımı Özeti

| Sprint | Alper | Arkadaş |
|--------|-------|---------|
| S0 ✅ | Scaffold + Tokens + FastAPI | Asset klasörü + ilk event JSON'ları |
| S1 ✅ | MapCanvas + Shader (kritik) | Berlin/Vienna manuel veri indirme |
| S2 ✅ | Globe + Intro + Loading | Wikidata event veri çekimi |
| S3 ✅ | Timeline + Events + EventPopup + ReplayButton | Event JSON doldurma (30–50 / şehir) |
| S4 ✅ | EraAudioEngine + FrequencyVisualizer | MP3 test + browser ses testi |
| S5 ✅ | CityDataLoader cache + FlyTo + BuildingPopup + eraColors + Globe day/night + lüks kartlar + bayraklar | NYC/Chicago GeoJSON temizleme |
| **ML-1** | **PLUTO + Geoportal spatial join pipeline (GeoPandas)** | **GHSL entegrasyonu + veri kalite kontrolü** |
| **ML-2** | **Feature engineering + XGBoost + PyTorch MLP eğitimi** | **Cross-city evaluation + confusion matrix raporu** |
| **ML-3** | **FastAPI /predict-era + /predict-city endpoint** | **Endpoint test + batch prediction doğrulama** |
| **ML-4** | **Frontend: provenance badge + AI predicted görsel** | **Filter panel UX + şehir karşılaştırma chart** |
| **NLP-1** | **Ollama kurulum + RAG pipeline (ChromaDB)** | **RAG quality test + domain veri chunk'lama** |
| **NLP-2** | **Function calling agent + FastAPI handler** | **Function call senaryoları test (10+ use case)** |
| **NLP-3** | **Chat UI komponenti + SSE streaming** | **Guided tour scriptleri + demo akışı** |
| S10 | Design review + final polish + demo | Teknik rapor (mimari + ML metodoloji + sonuçlar) |

> **Durum özeti (2026-06-21):** SDP1 S0–S5 **TAMAMEN** tamamlandı. UI altyapısı bitirme projesi için hazır. Şehirler: 11 (NY/Chicago/Berlin/Vienna/Paris/London/Barcelona/Madrid/Tokyo/Moscow/İstanbul). Veri analizi: NY %98 year, Berlin %10, diğerleri <%6 — PLUTO+GHSL ile zenginleştirilecek. **Yeni vizyon onaylandı (2026-06-21):** Çok şehirli bina era tahmin ML modeli (XGBoost/MLP, tabular geometrik features) + Llama 3.1 8B local RAG chatbot (function calling ile app state kontrolü) + data provenance katmanı (PLUTO/Geoportal/GHSL/AI badge'leri). Danışman: 3 ML/AI geçmişli hoca, Amerika geçmişli — akademik rigor bekleniyor. Sıradaki: ML-1 veri mühendisliği (PLUTO pipeline).

> **Durum özeti (2026-07-22):** SDP1 S0–S5 + v0.3 ara sprint (görsel cila + performans) tamam. **ML-1/2/3 tamam**: 43.5K etiketli bina, XGBoost CV F1=0.561 (cross-city bulgular belgeli), 3 inference endpoint çalışıyor. Events: **11/11 şehir akademik İngilizce + APA + references.md**. Müzik: motor hazır, mp3 yok — `FEATURES.music=false`. Sürüm 0.3.0, master push güncel (`546fa20`). **Sıradaki: ML-4 frontend entegrasyonu** (provenance badge, AI tahmin katmanı, filtre paneli — backend hazır, frontend'de sıfır /api çağrısı var!) + NLP capstone (Ollama+RAG). Bilinen borçlar Fable_Advice.md'de: GeoJSON diyet+brotli (2.2), era histogram (1.5), metodoloji modal (1.7), i18n (3.2), loading gerçek % (3.5), Vitest+CI (1.11). Backend taşınabilirlik fix'i gerekli: `main.py:237` predict.parquet yolu hardcode (`D:\PROJELER\ml_data`).
