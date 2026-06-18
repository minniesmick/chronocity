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

**Sprint 0 + Sprint 1 tamamlandı.** Scaffold + 3D çekirdek çalışıyor, NYC verisi doğrulandı.

- **Typography**: Space Grotesk (heading/mono) + Inter (body) — `src/styles/tokens.css`'te sabitlendi
- **Colors**: `#0A0A0F` zemin, `#F59E0B` amber aksan, `#E2E8F0` metin, `#1E293B` panel — tokens'ta sabitlendi. Şehir renkleri: istanbul=#f59e0b, new-york=#3b82f6, chicago=#8b5cf6, berlin=#10b981, vienna=#ef4444
- **Spacing**: 4px base grid — `--space-{1-8}` scale tokens'ta tanımlı
- **Stack**: React 18 + Vite 5 + TS scaffold ✅. Zustand 5 global store (t/activeCity/era/isDayMode/isPlaying/activeEvent/audioReady) ✅. FastAPI backend `/ws` + CORS ✅.
- **3D Çekirdek**: deck.gl 9 GeoJsonLayer — NYC 6.550 bina, `construction_year` morph (t→yıl 1800–2026), GPU transitions 400ms. LightingEffect gündüz (sıcak, 1.4) / gece (soğuk, 0.5). ✅
- **Tamamlanan componentler**: `MapCanvas`, `DayNightToggle`, `DevTimeScrubber` (geçici), `CityExperience`, `useCityBuildings` hook ✅
- **Veri**: NYC `buildings.geojson` (3.4MB, `height`+`construction_year`, 6.550 bina Midtown/Flatiron). Diğer şehirler → `hasBuildingData: false` no-op stratejisi.
- **Sıradaki**: Sprint 2 (SDP1 devam ediyor) — GlobeSelector + IntroScene + CityLoadingScreen + React Router. Tek şehir verisi var (NYC), diğerleri veri geldikçe eklenecek.

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
| **SunShadowEngine** | **SDP2** | **Ray-casting + quadtree spatial index. "Çatı panele uygun mu?" / "Sabah güneşi alır mı?" hesaplamalı geometri.** |
| **MultiCriteriaRouter** | **SDP2** | **OSM graf + A*/Dijkstra + Pareto çok-kriterli optimizasyon. En sessiz/güneşli/yeşil yürüyüş rotası.** |
| **UrbanGrowthML** | **SDP2** | **construction_year etiketli veri → spatial ML → "şehir nereye yoğunlaşacak?" GNN bina-komşuluk grafı.** |
| **NLSpatialAgent** | **SDP2** | **"Su kenarında 1920 öncesi 50m+ bina göster" → spatial sorgu. LLM tool-use + RAG + mekânsal DB.** |
| **TrafficSimulation** | **SDP2 stretch** | **Agent-based simülasyon + GPU compute. "30dk sonra burası tıkanır mı?" Teknik tavan en yüksek.** |

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
