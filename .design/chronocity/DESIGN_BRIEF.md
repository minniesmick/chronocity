# Design Brief: ChronoCity

## Problem

Şehirler dönüşür — ama bu dönüşüm genellikle sayılar, arşiv fotoğrafları veya akademik raporlar olarak kalır. Kimse o dönüşümü **hissedemez**: 1960 Berlin'in sesi neydi, 1980 İstanbul'un silueti nasıldı, New York'un 2000'lerdeki enerjisi ne kadar farklıydı? Mevcut araçlar ya salt veri (GIS yazılımları) ya da salt görsel (fotoğraf arşivleri) sunar. İkisini birleştiren, üstüne ses ve gerçek zamanlı interaksiyon ekleyen bir deneyim yoktur.

## Solution

ChronoCity; New York, Chicago, Berlin, Viyana ve İstanbul'un kentsel dokusunu zaman içinde 3D olarak gezmeyi, her dönemin ses kimliğini procedural olarak duymayı ve canlı verilerle şehrin bugünkü nabzını hissetmeyi tek bir web deneyiminde sunar. Kullanıcı bir zaman kaydırıcısı çektiğinde bina silüetleri morph eder, renkler kayar, ambient müzik çağa geçiş yapar — hepsi aynı `t` parametresiyle senkronize, model yok, pure kod.

## Experience Principles

1. **Senkronize duyusal katmanlar > ayrı ayrı özellikler** — Görsel, ses ve veri aynı anda, aynı parametreyle değişir. Hiçbir zaman "şimdi müziği değiştir" butonu yoktur; zaman kaydırılınca her şey birlikte akar.

2. **Performans = sanat kararı** — 60fps shader render, düşük latency WebSocket sync ve optimized geometry yalnızca teknik hedef değil; akıcılık bizzat estetik deneyimin parçasıdır. Takılma = sanatın bozulması.

3. **Kontrol derinliği, progressive disclosure ile** — İlk bakışta sinematik ve sade. Kullanıcı keşfettikçe katman panelleri, frekans ekolayzerı, şehir karşılaştırması açılır. Jüri demosu için ilk 30 saniye wow, sonraki 5 dakika derinlik.

## Aesthetic Direction

- **Philosophy**: Tekno-sinematik minimalizm — koyu zemin, tek aksan rengi (amber/ember), yüksek kontrast veri etiketi, WebGL ışık efektleri. Winamp3 kontrol yoğunluğu + Google Earth Studio sinematizmi + Are.na kültürel derinliği.
- **Tone**: Dramatik, epik, hafif melankolik. Bir şehrin geçmişine saygı duruşu gibi. Soğuk değil — sıcak amber tonlarla insancıl.
- **Reference points**:
  - [Winamp3 / Milkdrop] → kontrol paneli yoğunluğu, visualizer estetiği
  - [Google Earth Studio] → 3D kamera hareketleri, bina extrusion dramatizmi
  - [Are.na] → kültürel katman, entelektüel his
  - [Resn.co / Active Theory] → interaktif web sanatı, yeni nesil UI
  - [Nuit Blanche Istanbul fotoğrafları] → nostaljik şehir hissi
- **Anti-references**:
  - Google Maps / Apple Maps klonu — turistik, steril
  - PowerPoint görünümlü akademik poster
  - Bootstrap/Material UI generic komponenti
  - Beyaz arka plan, mavi buton

## Existing Patterns

**S0+S1+S2+S3(kısmi) tamamlandı. 11 şehir verisi hazır.** Tüm temel akış + timeline + event noktaları + animated ikonlar çalışıyor.

- **Typography**: Space Grotesk (heading/mono) + Inter (body) — `src/styles/tokens.css`
- **Colors**: `#0A0A0F` zemin, `#F59E0B` amber, `#E2E8F0` metin — tokens. Şehir renkleri: istanbul=#f59e0b, new-york=#3b82f6, chicago=#8b5cf6, berlin=#10b981, vienna=#ef4444 (diğerleri cities.ts'te)
- **Stack**: React 18 + Vite 5 + TS. Zustand 5 store: `t/activeCity/era/isDayMode/isPlaying/activeEvent/audioReady/activeBuilding`. FastAPI `/ws` + CORS. Framer Motion v11.
- **3D Çekirdek**: deck.gl 9 GeoJsonLayer — 11 şehir, `construction_year` morph, GPU transitions 400ms. LightingEffect gündüz/gece + FlyToInterpolator (zoom=5→14.5, 2.2s) ✅
- **Era Renk Sistemi**: `colorByEra(year)` 7 dönem + `colorUndated(frame)` RAF pulse → `src/lib/buildingColors.ts`. Paylaşımlı: `src/lib/eraColors.ts` (BuildingPopup + TimelineBar pill + GlobeSelector senkronize) ✅
- **Zaman lib**: `src/lib/time.ts` — `yearFromT`, `tFromYear` (clamped 0–1), `eraFromYear`, `YEAR_MIN=1800`, `YEAR_MAX=2026` ✅
- **Routing**: React Router v6 — `/` IntroScene, `/globe` GlobeSelector, `/city/:id` CityExperience. AnimatePresence mode="wait" ✅
- **CSS mimarisi**: `sprint1.css` (MapCanvas + CityExp + DayNight + TimelineBar + EventMarker), `sprint2.css` (IntroScene + GlobeSelector + CityLoadingScreen). Token-driven, no hardcode. ✅
- **Animated Icons**: `src/components/icons/` — 31 adet Framer Motion animated SVG. Props: `size`, `color`, `strokeWidth`, `className`. Handle: `AnimatedIconHandle { startAnimation, stopAnimation }`. Kaynak: `framer-motion` (not motion/react). ✅
- **Tamamlanan componentler**:
  - `MapCanvas` (deck.gl), `DayNightToggle` (icon entegre), `CityExperience` (header slide-down + icon back butonu), `useCityBuildings` hook ✅
  - `GlobeSelector` (Three.js, scale-in 0.82→1.0, ambient glow, raycaster click, **gündüz/gece texture swap** earth-night.jpg↔earth-day.jpg, **lüks .globe-city-card** glassmorphism, bayrak+şehir+ülke, downward triangle pointer, city-color left border, DayNightToggle overlay) ✅
  - `IntroScene` (scanlines, stagger animasyon, exit fade) ✅
  - `CityLoadingScreen` (typewriter milestones, progress bar, AnimatePresence exit) ✅
  - `TimelineBar` (glassmorphism, play/pause, era pills **era-color CSS var ile dönem renginde**, keyboard nav, auto-play) ✅
  - `EventMarker` (proximity fade, pulse, click→setActiveEvent) ✅
  - `EventPopup` (glassmorphism slide-up, FM animate prop, ESC/X/dışarı) ✅
  - `ReplayButton` (amber floating, RefreshIcon) ✅
  - `EraAudioEngine` / `useEraAudio` (Web Audio API A/B crossfade, autoplay-safe) ✅
  - `FrequencyVisualizer` (AnalyserNode 64-bin, Canvas 2D 32-bar amber, mix-blend-mode screen) ✅
  - `BuildingPopup` (lüks glassmorphism, 46px mono yükseklik, era accent border, animated bar, eraColors) ✅
  - `useCityEvents` hook (activeCity → fetch `/cities/{id}/events/info.json`) ✅
- **Event verisi**: Berlin (9 olay 1871–2006) + İstanbul (9 olay 1856–2010) → `public/cities/{city}/events/info.json` ✅
- **Müzik klasörleri**: 11 şehir × 4 era = 44 placeholder → `/public/cities/{city}/music/{eraId}.mp3` ✅
- **Veri (11 şehir, tümü `hasBuildingData: true`, `public/cities/{id}/buildings.geojson`):**
  - NYC 6.5K bina 3.4MB | Berlin 27.5K 12MB | Vienna 18K 8.3MB | Chicago 4.5K 1.6MB
  - İstanbul 5K 1.4MB | Paris 13.7K 6MB | London 26.9K 9.5MB | Tokyo 26K 7.4MB
  - Madrid 14.2K 6.2MB | Barcelona 19.5K 8.4MB | Moscow 8.2K 3.2MB
- **Veri analizi (construction_year doluluk):** NY=%98, Berlin=%10, Moscow=%6, Paris=%4, diğerleri<%2. Height=%99-100 hepsinde. → PLUTO+Geoportal+GHSL ile zenginleştirilecek.
- **Sıradaki**: CAPSTONE ML-1 → PLUTO spatial join pipeline. Bbox genişletme ML-1 sonrasına bırakıldı (pipeline önce küçük datasette doğrulanacak).

## User Flow (Ekran Sırası)

```
[1. INTRO]
  Video loop (stock/AI, şehirsiz evrensel)
  → Kısa fade, logo animasyonu
  → "Enter" veya scroll ile geç

[2. GLOBE]
  Interaktif 3D Dünya modeli (Three.js Globe)
  5 şehir: ışıklı nokta + şehre özel renk
  Hover → ok/pulse animasyonu + şehir adı type-on
  Duran animasyon: şehir adları hafifçe dalgalanır
  Ülke bayrakları küçük, şehir noktasının yanında
  Şehre tıkla → loading ekranına geç

[3. CITY LOADING]
  Seçilen şehre özel video (stock veya AI)
  Üstüne şehir istatistikleri/tarihi bilgiler animasyonla yazar
  (nüfus, kuruluş yılı, önemli dönüm noktaları — typewriter effect)
  Bu sürede 3D veri + asset'ler arka planda yüklenir
  Progress bar ince ve minimal, videonun altında

[4. MAIN EXPERIENCE]
  Tam ekran 3D harita + tüm interaktif katmanlar
  Scroll-animated popup'lar: kullanım ipuçları (ilk girişte)
  Kontroller: Gece/Gündüz toggle, Yıl göstergesi, Radyo butonu
  Timeline bar (tam genişlik, üst veya alt)
  Replay butonu → intro animasyonlarını baştan oynatır

[5. TIMELINE MODE]
  Kullanıcı timeline'ı aktif eder veya otomatik çalar
  Zaman akarken tarihsel olaylar belirir
  Olay tipleri: Kötü (kırmızı alert), İyi (yeşil), Nötr/Önemli (amber)
  Olaya tıkla → kısa bilgi popup
  "Daha fazla" → Gemini API ile detaylı anlatı
  Müzik durmaz, zaman dursa bile ses devam eder
```

## Asset Yapısı (Statik Dosyalar)

```
/public/cities/
  istanbul/
    loading-video.mp4        ← şehre özel loading videosu
    events/
      1999-08-17/
        info.json            ← {date, title, description, type, category}
        cover.jpg            ← tek görsel
      1453-05-29/
        ...
    music/
      1960s.mp3
      1980s.mp3
      2000s.mp3
      modern.mp3
  new-york/
    ...
  chicago/
    ...
  berlin/
    ...
  vienna/
    ...
```

### Olay Verisi Formatı (info.json)

```json
{
  "date": "1999-08-17",
  "title": "Marmara Depremi",
  "shortDesc": "7.6 büyüklüğündeki deprem 17.000'den fazla can aldı.",
  "type": "negative",
  "category": "disaster",
  "coordinates": [40.76, 29.97],
  "wikiSlug": "1999_İzmit_depremi"
}
```

`type`: `"positive"` | `"negative"` | `"neutral"`
Veri kaynağı: Wikidata API (yarı otomatik çekim) → manuel düzenleme → JSON

## Component Inventory

| Component | Status | Notes |
|-----------|--------|-------|
| MapCanvas | ✅ Built (S1) | deck.gl standalone, pitch 50°, LightingEffect gündüz/gece, NYC 6550 bina |
| DayNightToggle | ✅ Built (S1) | Segmented buton, 800ms CSS geçiş, lighting swap |
| DevTimeScrubber | ✅ Built (S1) | Geçici dev aracı — TimelineBar (S3) ile değiştirilecek |
| CityExperience | ✅ Built (S1) | Sprint 1 sahne kabuğu — S2 router ile sarmalanacak |
| IntroScene | S2 | Video loop, logo fade, enter CTA |
| GlobeSelector | S2 | Three.js 3D dünya, 5 şehir noktası, hover animasyonu, bayraklar |
| CityLoadingScreen | S2 | Şehre özel video + typewriter istatistik + progress bar |
| TimelineBar | S3 | Tam genişlik, yatay, üst veya alt konumlandırılabilir |
| EventMarker | S3 | Timeline üstünde olay noktası — 3 renk tipi (kırmızı/yeşil/amber) |
| EventPopup | S3 | Tıklanınca kısa bilgi + görsel, "Daha fazla" → Gemini |
| YearIndicator | S3 | Aktif yılı gösteren minimal sayısal gösterge |
| RadioButton | S3 | Şehre ait era müziği manuel seçimi |
| ReplayButton | S3 | Tüm giriş animasyonlarını baştan oynatır |
| EraAudioEngine | S4 | MP3 dosyaları + Web Audio API crossfade, zaman dursa müzik devam eder |
| FrequencyVisualizer | S4 | Web Audio FFT → ambient görsel halka |
| BuildingPopup | S6 | Tıklanan bina: dönem, yükseklik, tarihsel not |
| LayerPanel | S6 | Veri katmanları toggle: trafik, nüfus, gürültü |
| FluidHeatmap | S6 | Navier-Stokes particle overlay |
| SoundNotePin | S7 | Kullanıcı ses notu bırakma, WebSocket sync |
| GeminiReportDrawer | S7 | Opsiyonel — olay detayı + bölge analiz raporu |
| OnboardingPopups | S8 | Scroll-triggered, ilk girişte UI ipuçları |
| StreetViewBlend | S8 | Street View + shader morph overlay |
| CompareMode | S8 | İki şehri / iki dönemi split-screen |
| PWAShell | S9 | Offline cache, install prompt, mobile layout |
| **EraMLPredictor** | **ML-2/3** | **XGBoost + PyTorch MLP. Girdi: footprint area/compactness/height/komşuluk stats. Çıktı: era sınıfı + confidence. FastAPI /predict-era endpoint.** |
| **ProvenanceBadge** | **ML-4** | **BuildingPopup'ta data_source badge: Altın=PLUTO, Gümüş=OSM, Bronz=GHSL, Mor=AI_Predicted.** |
| **DataSourceFilter** | **ML-4** | **Layer toggle: "Sadece doğrulanmış" / "AI dahil" / "Hepsini göster". MapCanvas legend.** |
| **AIChatGuide** | **NLP-3** | **Sağ kenar açılır panel. Llama 3.1 8B local + RAG (ChromaDB) + function calling (set_city, set_year, highlight_era). SSE streaming.** |

## Key Interactions

**Globe → Şehir Seçimi**
GlobeSelector'da şehir noktasına tıklanır →
- Globe kamera zoom-in + fade
- CityLoadingScreen geçişi (video + typewriter stats)
- Arka planda: 3D bina verisi, MP3'ler, event JSON'ları yüklenir
- Progress tamamlanınca → MainExperience açılır

**Zaman Kaydırma (Ana Interaction)**
TimelineBar sürüklenir veya otomatik çalar →
- `t` parametresi (0.0–1.0) tüm sisteme yayılır
- Bina extrusion geometry lerp eder
- GLSL shader mix() ile blend
- MP3 crossfade (era_A → era_B), zaman dursa da müzik devam eder
- EventMarker'lar o tarihe yaklaştıkça fade-in olur

**Olay Interaction**
EventMarker'a tıklanır →
- EventPopup açılır: başlık + kısa açıklama + kapak görseli
- "Daha fazla" butonuna basılır → GeminiReportDrawer slide-in
- Gemini streaming response satır satır render edilir

**Gece / Gündüz Toggle**
DayNightToggle'a basılır →
- GLSL shader uniform değişir (ambient light, texture blend)
- Geçiş 800ms smooth lerp, anında değil

**Replay**
ReplayButton'a basılır →
- Mevcut harita freeze
- IntroScene overlay olarak açılır, video + animasyonlar baştan
- Kapanınca harita kaldığı yerden devam

**Ses Notu Bırakma**
Haritada konuma uzun basılır →
- Pin animasyonla düşer
- Mikrofon izni → kayıt → WebSocket broadcast
- Diğer kullanıcılar hover'da duyar

**Katman Toggle**
LayerPanel'de katman açılır →
- FluidHeatmap animate-in
- IBB/OpenData API lazy fetch
- Particle yoğunluğu veriye göre ayarlanır

## Responsive Behavior

| Breakpoint | Davranış |
|------------|---------|
| Desktop ≥1280px | Tam deneyim — tüm paneller görünür, 3D full |
| Tablet 768–1279px | LayerPanel collapsed, TimeSlider bottom bar'a taşır |
| Mobile PWA <768px | Sadece harita + zaman slider + şehir seçici. 3D extrusion basitleştirilir (LOD düşürülür). Ses çalışır. |

Desktop öncelikli geliştirme — mobile PWA ikinci sprint.

## Accessibility Requirements

- Kontrast oranı minimum 4.5:1 (WCAG AA) — amber on dark sağlanmalı
- TimeSlider keyboard navigable (←/→ ok tuşları, 5% adım)
- Tüm ikonlar SVG + aria-label
- Harita üzerindeki interaktif elementler focus ring alır
- Ses otomatik başlamaz — kullanıcı ilk etkileşimden sonra başlar (Web Audio autoplay policy)
- `prefers-reduced-motion` → shader morph kapatılır, instant switch

## Müzik Stratejisi

- **Birincil:** Gerçek MP3 dosyaları — her şehir için 4 era (1960s / 1980s / 2000s / modern)
- **Fallback:** Royalty-free stock (jüri telif sorunu çıkarırsa)
- **Format:** `/public/cities/{city}/music/{era}.mp3`
- **Playback:** Web Audio API ile crossfade, zaman slider dursa bile müzik çalmaya devam eder
- **Toplam:** 5 şehir × 4 era = 20 MP3 dosyası (her biri ~2–3 dk loop)

## Tarihsel Olay Verisi Stratejisi

- **Başlangıç:** Wikidata SPARQL API → şehir + tarih aralığı sorgusu → JSON export → manuel düzenleme
- **Fallback:** Manuel JSON yazımı (zaman baskısı olursa)
- Her şehir için hedef: **30–50 önemli olay**, iyi dağılmış tarih aralığında
- Her olay: `info.json` + `cover.jpg` → `/public/cities/{city}/events/{date}/`
- Olay tipleri: `positive` (yeşil) / `negative` (kırmızı) / `neutral` (amber)

## Out of Scope

- Kullanıcı hesabı / authentication (ses notları anonim)
- Backend veri depolama (WebSocket ephemeral, not persist)
- Mobil native app (Flutter companion ikinci aşama, bu brief dışı)
- AR/VR modu
- Gerçek zamanlı canlı trafik API entegrasyonu (simüle veri yeterli MVP için)
- Tarihsel fotoğraf telif hakkı yönetimi (Wikimedia Commons lisanslılar kullanılır)
- i18n / çoklu dil desteği
- B kullanıcısı (akademisyen/şehir plancısı) için özel analitik araçlar
- 50'den fazla olay per şehir (MVP için)

---

## Teknik Stack (Referans)

```
Frontend    React 18 + Vite + TypeScript
3D/Maps     deck.gl + Three.js + Google Maps JS API
Shader      GLSL (WebGL2)
Audio       Web Audio API + Tone.js
Animation   Framer Motion + GSAP (kamera)
Realtime    WebSocket (FastAPI backend)
Data        OSM Overpass API, IBB Open Data, NYC Open Data, CityGML
Optional    Gemini API (raporlama)
PWA         Vite PWA plugin
```

## Şehir Veri Kaynakları

| Şehir | 3D Bina | Tarihi Katman | Canlı Veri |
|-------|---------|---------------|------------|
| New York | NYC CityGML LOD2 (TUM) + OSM | NYC Open Data zaman serisi | 311 API |
| Chicago | OSM + Microsoft footprints | City of Chicago Data Portal | Chicago Data Portal |
| Berlin | Almanya LOD1-LOD2 (56M bina) | Landesarchiv Berlin | Berlin Open Data |
| Viyana | Viyana LOD1+2 açık | Wien Geschichte Wiki | data.gv.at |
| İstanbul | OSM (height tag'li binalar) | IBB Açık Veri + Istanbul Urban DB | data.ibb.gov.tr |
