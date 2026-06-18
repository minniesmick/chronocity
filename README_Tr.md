<a id="top"></a>

<div align="right">

🇬🇧 [English](./README.md)

</div>

<div align="center">

# ChronoCity

**5 şehirde 226 yıllık kentsel tarihi gerçek zamanlı ve 3 boyutlu olarak keşfet.**

![Sürüm](https://img.shields.io/badge/sürüm-0.1.0-f59e0b?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Web-3b82f6?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20deck.gl%20%2B%20Three.js-8b5cf6?style=flat-square)
![Lisans](https://img.shields.io/badge/lisans-MIT-e0aaff?style=flat-square)
![Node](https://img.shields.io/badge/node-18%2B-10b981?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-ef4444?style=flat-square)

> ChronoCity; İstanbul, New York, Chicago, Berlin ve Viyana'nın mimari evrimini canlı bir 3D deneyim olarak render eder. 1800–2026 arasındaki zaman çizelgesini sürükle, binaların gerçek zamanlı yükselişini izle. Yükseklik, renk ve ortam müziği tek bir `t` parametresiyle birlikte morph eder. Bilgisayar Mühendisliği bitirme projesi olarak inşa edildi (SDP1 + SDP2).

</div>

---

## İçindekiler

- [Genel Bakış](#genel-bakış)
- [Özellikler](#özellikler)
- [Ekran Görüntüleri](#ekran-görüntüleri)
- [Teknoloji Stack'i](#teknoloji-stacki)
- [Gereksinimler](#gereksinimler)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Yapılandırma](#yapılandırma)
- [Geliştirme](#geliştirme)
- [Build ve Paketleme](#build-ve-paketleme)
- [Proje Yapısı](#proje-yapısı)
- [Yol Haritası](#yol-haritası)
- [Katkı](#katkı)
- [Yazar](#yazar)
- [Lisans](#lisans)

---

## Genel Bakış

ChronoCity, tarayıcı tabanlı bir 3D kentsel zaman yolculuğu deneyimidir. Açık coğrafi verilerden gerçek bina footprint'leri ve yükseklikleri render eder, her binayı inşa yılına göre kapılar ve kullanıcı zamanı gezdirirken tüm silueti morph eder. 3D geometri, ortam müziği ve parçacık overlay'leri — her duyusal katman tek bir normalize edilmiş `t` değeriyle (0.0 = 1800, 1.0 = 2026) sürülür; bu da sistemi yeni şehir ve veri kaynaklarına kolayca genişletilebilir kılar.

Proje iki akademik dönemde yürütülür: SDP1 görselleştirme motorunu kurar, SDP2 hesaplamalı analitik katman ekler (gölge analizi, çok-kriterli rota, mekânsal ML, doğal dil sorgu ajanı).

---

## Özellikler

### 3D Şehir Motoru
- Gerçek GeoJSON footprint'lerinden extrude edilmiş bina geometrisi (NYC: 6.550 bina, Midtown/Flatiron)
- `construction_year` kapısı — her bina yalnızca aktif yıl kendi inşa tarihine ulaşınca belirir
- deck.gl aracılığıyla GPU hızlandırmalı geçişler (yükseklik + renk, 400 ms)
- Sinematik kamera varsayılanları: pitch 50°, bearing −20°, zoom 14.5, maxPitch 75°

### Zaman Morphing
- Tek `t` parametresi (0.0–1.0) lineer olarak 1800–2026 yıllarına eşlenir
- Tüm katmanlar (geometri, ışıklandırma, ses, parçacıklar) senkronize kalır
- İleri/geri kaydır — binalar gerçek zamanlı yükselir ve solar
- Timeline otomatik oynatma modu (isPlaying state)

### Gece / Gündüz Modu
- Sıcak gündüz: AmbientLight 1.1 + DirectionalLight 1.4 (soft sarı)
- Serin gece: AmbientLight 0.5 + DirectionalLight 0.7 (mavi-beyaz)
- deck.gl ışıklandırma değişimiyle senkronize 800 ms CSS arka plan geçişi
- Gece modunda kısa binalar kararır, amber kor efekti ön plana çıkar

### Çok Şehirli Mimari
- `hasBuildingData` flag'iyle şehir kaydı — verisi olmayan şehirler seçilebilir ama hiçbir şey render etmez (graceful no-op)
- Şehir başına lazy GeoJSON fetch; ilk yükleme sonrası cache'lenir
- Şehre özel renk kimliği: İstanbul amber, NYC mavi, Chicago mor, Berlin yeşil, Viyana kırmızı

### Ortam Ses Motoru *(Sprint 4 — planlandı)*
- Web Audio API + Tone.js: era MP3'leri arasında crossfade (1960s / 1980s / 2000s / modern)
- Timeline duraklatılsa bile ses devam eder
- Frekans visualizer halkası (AnalyserNode → FFT → Canvas)

### Tarihsel Olaylar *(Sprint 3 — planlandı)*
- Zaman çizelgesinde olay işaretleri (pozitif / negatif / nötr)
- Tıklayınca detay popup açılır; "Daha fazla" Gemini akışlı rapor tetikler

### SDP2 Analitik Katman *(planlandı)*
- **Güneş/gölge motoru** — ray-casting + quadtree spatial index; "hangi çatı güneş paneline uygun?" sorusunu yanıtlar
- **Çok-kriterli rota motoru** — A\*/Dijkstra + Pareto optimizasyonu; en sessiz/güneşli yürüyüş rotasını bulur
- **Kentsel büyüme ML** — construction_year verisi üzerinde mekânsal ML; yoğunlaşma yönünü tahmin eder
- **Doğal dil mekânsal ajanı** — "Su kenarında 1920 öncesi 50m+ binaları göster" → anında sorgu

---

## Ekran Görüntüleri

> Ekran görüntüleri yakında — şimdilik uygulamayı yerel olarak çalıştırın.

Sprint 1 doğrulandı: NYC 2026 tam siluet, NYC 1900 seyrek siluet, gündüz sıcak ışık, gece koyu amber kor.

---

## Teknoloji Stack'i

| Katman | Teknoloji | Sürüm |
|--------|-----------|-------|
| Frontend framework | React | 18.3 |
| Build aracı | Vite | 5.4 |
| Dil | TypeScript | 5.6 |
| 3D harita motoru | deck.gl | 9.0 |
| 3D küre | Three.js | 0.169 |
| Harita tile | MapLibre GL | 4.7 |
| State yönetimi | Zustand | 5.0 |
| Animasyon (UI) | Framer Motion | 11 |
| Animasyon (kamera) | GSAP | 3.12 |
| Ses motoru | Tone.js | 15 |
| Backend | FastAPI | güncel |
| Gerçek zamanlı | WebSocket (FastAPI /ws) | — |
| Routing | React Router | 6 |

**İletişim:** Frontend (Vite :5173), `/api` ve `/ws` isteklerini FastAPI'ye (:8000) proxy eder. Sprint 1 için Google Maps veya Mapbox API anahtarı gerekmez — deck.gl koyu arka plan üzerinde standalone render eder.

---

## Gereksinimler

| Gereksinim | Sürüm | Not |
|------------|-------|-----|
| Node.js | 18+ | LTS önerilir |
| npm | 9+ | Node ile gelir |
| Python | 3.11+ | FastAPI backend için |
| pip | 23+ | — |
| Git | herhangi | — |

3D şehir görünümü için Google Maps veya Mapbox API anahtarı gerekmez.

---

## Hızlı Başlangıç

```bash
# 1. Repoyu klonla
git clone https://github.com/minniesmick/chronocity.git
cd chronocity

# 2. Frontend bağımlılıklarını kur
npm install

# 3. Frontend dev server'ı başlat
npm run dev
# → http://localhost:5173
```

```bash
# 4. (Opsiyonel) FastAPI backend'i başlat (ayrı terminal)
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

[http://localhost:5173](http://localhost:5173)'i aç, **New York**'u tıkla (tek verili şehir), zaman scrubber'ını sürükle.

---

## Yapılandırma

### Vite proxy (`vite.config.ts`)

```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws':  { target: 'ws://localhost:8000', ws: true }
  }
}
```

### Yeni şehir ekleme

1. `public/cities/{sehir-id}/` altına `buildings.geojson` ekle. Property formatı: `{ height: number, construction_year: number | null, name: string | null }`
2. `src/data/cities.ts`'e `hasBuildingData: true` ile şehri kaydet
3. `src/styles/tokens.css`'den şehir rengi seç ya da yeni token ekle

### Global state (`src/store/useStore.ts`)

| Anahtar | Tip | Varsayılan | Açıklama |
|---------|-----|-----------|---------|
| `t` | `number` | `1` | Normalize zaman 0.0–1.0 → yıl 1800–2026 |
| `activeCity` | `CityId \| null` | `null` | Seçili şehir |
| `era` | `EraId` | `"modern"` | Ses dönemi |
| `isDayMode` | `boolean` | `true` | Gündüz/gece ışıklandırma |
| `isPlaying` | `boolean` | `false` | Timeline otomatik oynatma |
| `activeEvent` | `CityEvent \| null` | `null` | Aktif tarihsel olay |
| `audioReady` | `boolean` | `false` | Web Audio API kilidi açıldı |

### Dev otomasyonu

Geliştirme ortamında `window.useStore` deterministik test için açılır:

```javascript
// NYC'yi 1902 gecesine atla
window.useStore.setState({ t: 0.045, isDayMode: false })
```

---

## Geliştirme

### Port haritası

| Servis | Port | Başlatma komutu |
|--------|------|----------------|
| Vite frontend | 5173 | `npm run dev` |
| FastAPI backend | 8000 | `uvicorn main:app --reload` |

### Kodlama kuralları

- Tüm renkler `src/styles/tokens.css`'teki CSS değişkenlerinden — hardcode hex yok
- Animasyonlarda `transform`/`opacity` — asla `width`/`height` (60 fps hedef)
- `t` tek saattir. Hiçbir duyusal katman için ayrı timer ekleme.
- deck.gl HMR zombie instance üretebilir. Harita render etmeyi bırakırsa dev server'ı yeniden başlat.

### Component ekleme

1. `src/components/` içinde duplicate kontrol et
2. İsimlendirme: `PascalCase.tsx` + eş konumlu `kebab-case.css`
3. Aktif sprint görevini [`.design/chronocity/TASKS.md`](.design/chronocity/TASKS.md)'den bak
4. Bitince görevi `[x]` olarak işaretle

---

## Build ve Paketleme

```bash
# 1. Type-check + frontend build
npm run build
# Çıktı: dist/ (~2 MB gzip asset'ler)

# 2. Production build'i yerel önizle
npm run preview
# → http://localhost:4173
```

Backend ayrıca deploy edilir (Railway, Render veya VPS). Frontend statik SPA'dır — Vercel, Netlify veya GitHub Pages'a hostlanabilir.

---

## Proje Yapısı

```
chronocity/
├── .design/                    # Tasarım dokümanları ve Claude Code skill'leri
│   └── chronocity/
│       ├── DESIGN_BRIEF.md     # Estetik yön, component envanteri
│       ├── TASKS.md            # Sprint görev listesi (S0–S10 + SDP2)
│       └── SKILL_MAP.md        # Hangi işlemde hangi design skill
├── backend/
│   ├── main.py                 # FastAPI: /ws WebSocket + /api/health + CORS
│   └── requirements.txt
├── public/
│   └── cities/
│       └── new-york/
│           ├── buildings.geojson   # 6.550 bina, height + construction_year
│           ├── events/             # Tarihsel olay JSON + kapak görselleri
│           └── music/              # Era MP3'leri (1960s/1980s/2000s/modern)
├── src/
│   ├── components/
│   │   ├── MapCanvas.tsx       # deck.gl 3D çekirdek, LightingEffect, GeoJsonLayer
│   │   ├── CityExperience.tsx  # Sprint 1 sahne kabuğu
│   │   ├── DayNightToggle.tsx  # Segmented gündüz/gece butonu
│   │   ├── DevTimeScrubber.tsx # Geçici dev scrubber (S3'te TimelineBar ile değişir)
│   │   └── sprint1.css         # Sahne + UI token-driven stiller
│   ├── data/
│   │   └── cities.ts           # Şehir kaydı (5 şehir, hasBuildingData flag)
│   ├── hooks/
│   │   └── useCityBuildings.ts # Lazy GeoJSON fetch hook
│   ├── lib/
│   │   ├── buildingColors.ts   # Yükseklik bazlı amber/ember renk rampası
│   │   └── time.ts             # yearFromT / tFromYear yardımcıları
│   ├── store/
│   │   └── useStore.ts         # Zustand global store
│   ├── styles/
│   │   ├── tokens.css          # Tüm CSS custom property'ler (renk, boşluk, yazı)
│   │   └── global.css          # Reset + base
│   ├── types.ts                # CityId, EraId, BuildingProperties, CityEvent
│   ├── App.tsx                 # Route: null → şehir seçici, şehir → CityExperience
│   └── main.tsx
├── .gitattributes
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## Yol Haritası

- [x] Sprint 0 — Scaffold: React + Vite + TS + Zustand + FastAPI + design token'lar
- [x] Sprint 1 — 3D çekirdek: deck.gl binalar, time morph (1800–2026), gece/gündüz toggle
- [ ] Sprint 2 — Giriş akışı: Three.js küre seçici, sinematik intro, şehir yükleme ekranı, React Router
- [ ] Sprint 3 — Zaman çizelgesi: tam genişlik scrubber bar, olay işaretleri, olay popup'ları
- [ ] Sprint 4 — Ses: era MP3 crossfade (Web Audio API + Tone.js), frekans visualizer
- [ ] Sprint 5 — Çok şehir: lazy data loader + fly-to animasyonu, İstanbul / Chicago / Berlin / Viyana verisi
- [ ] Sprint 6 — Katmanlar: fluid heatmap (Navier-Stokes parçacıklar), katman toggle paneli, bina popup
- [ ] Sprint 7 — Gerçek zamanlı: WebSocket ses notu (pin + kayıt + broadcast), Gemini rapor drawer
- [ ] Sprint 8 — Cila: onboarding tooltip, Street View blend, karşılaştırma modu (split-screen)
- [ ] Sprint 9 — PWA: offline cache, kurulum prompt, mobil layout, tablet responsive
- [ ] Sprint 10 — QA: cross-browser testi, Lighthouse audit, jüri demo scripti
- [ ] SDP2 — Analitik: güneş/gölge motoru, çok-kriterli rota, kentsel büyüme ML, NL mekânsal ajan

---

## Katkı

Bu bir akademik bitirme projesidir. Veri, hata raporu ve öneri katkıları memnuniyetle karşılanır.

```bash
# 1. Fork et ve klonla
git clone https://github.com/minniesmick/chronocity.git

# 2. Feature branch oluştur
git checkout -b feature/ozelligim

# 3. Değişiklikleri commit et
git commit -m "feat: ne yaptığını ve neden açıkla"

# 4. Push et ve PR aç
git push origin feature/ozelligim
```

**Projeye özel notlar:**
- `src/styles/tokens.css`'teki token'ları kullan — hardcode renk veya piksel değeri yok
- Önce Chromium tabanlı tarayıcıda test et (deck.gl WebGL2 davranışı motorlar arasında farklılık gösterir)
- Yeni şehir eklerken `height` (metre) ve `construction_year` (integer) içeren işlenmiş `buildings.geojson` dahil et

---

## Yazar

**Alper Yusuf Yaman**
[@minniesmick](https://github.com/minniesmick) on GitHub

---

## Lisans

[MIT Lisansı](./LICENSE) altında lisanslanmıştır.

© 2026 Alper Yusuf Yaman. İzin ücretsiz olarak verilmektedir; bu yazılımın bir kopyasını edinen herhangi bir kişi, yazılımı kopyalama, değiştirme, birleştirme, yayımlama, dağıtma, alt lisanslama ve/veya satma hakları dahil olmak üzere sınırlama olmaksızın kullanabilir.

---

<div align="center">
  <sub>Şehirler her şeyi hatırlar. ChronoCity, onlarla birlikte hatırlamanı sağlar.</sub>
  <br/><br/>
  <a href="#top">↑ en başa dön</a>
</div>
