<a id="top"></a>

<div align="right">

🇬🇧 [English](./README.md)

</div>

<div align="center">

# ChronoCity

**11 şehirde 226 yıllık kentsel tarihi gerçek zamanlı ve 3 boyutlu olarak keşfet.**

![Sürüm](https://img.shields.io/badge/sürüm-0.3.0-f59e0b?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Web-3b82f6?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%2019%20%2B%20deck.gl%20%2B%20FastAPI-8b5cf6?style=flat-square)
![Lisans](https://img.shields.io/badge/lisans-MIT-e0aaff?style=flat-square)
![Node](https://img.shields.io/badge/node-18%2B-10b981?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-ef4444?style=flat-square)

> ChronoCity, 11 dünya şehrinin mimari evrimini canlı bir 3D deneyim olarak render eder. 1800–2026 arasındaki zaman çizelgesini sürükle — binalar gerçek zamanlı yükselir, dönem müziği çalar ve XGBoost/MLP modeli her binanın inşa dönemini geometri ve kentsel bağlamdan tahmin eder. Bilgisayar Mühendisliği bitirme projesi (Bitirme Projesi 1 + 2) olarak geliştirildi.

</div>

---

## İçindekiler

- [Genel Bakış](#genel-bakış)
- [Özellikler](#özellikler)
- [ML Capstone](#ml-capstone)
- [Teknoloji Stack'i](#teknoloji-stacki)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [ML Kurulumu](#ml-kurulumu)
- [API Referansı](#api-referansı)
- [Proje Yapısı](#proje-yapısı)
- [Yol Haritası](#yol-haritası)
- [Yazar](#yazar)
- [Lisans](#lisans)

---

## Genel Bakış

ChronoCity, tarayıcı tabanlı bir 3D kentsel zaman yolculuğu deneyimidir. Açık coğrafi verilerden gerçek bina footprint'leri ve yükseklikleri render eder, her binayı inşa yılına göre kapılar ve kullanıcı zamanı gezdirirken tüm silueti morph eder. 3D geometri, ortam müziği ve parçacık overlay'leri — her duyusal katman tek bir normalize edilmiş `t` değeriyle (0.0 = 1800, 1.0 = 2026) sürülür.

Proje iki izden oluşur:

- **SDP1 (S0–S5)** — 3D görselleştirme motoru: küre seçici, zaman çizelgesi, ses, çok-şehirli
- **Capstone ML** — Dönem tahmini: 11 şehirde 43.500 etiketli bina, XGBoost + PyTorch MLP, FastAPI çıkarım uç noktaları

---

## Özellikler

### 3D Şehir Motoru
- Gerçek GeoJSON footprint'lerinden extrude edilmiş bina geometrisi — 11 şehirde **170.000+ bina**
- `construction_year` kapısı: her bina yalnızca aktif yıl kendi inşa tarihine ulaşınca belirir
- GPU hızlandırmalı geçişler (yükseklik + renk, 400 ms) deck.gl aracılığıyla
- Sinematik kamera varsayılanları: pitch 50°, bearing −20°, zoom 14.5

### Küre ve Giriş Animasyonu
- Galaksi giriş animasyonu: kamera derin uzaydan (z=30) Dünya'ya (z=18) 105 karede cubic ease-out ile uçar
- 1800 beyaz yıldız + 380 Samanyolu mavi tonlu yıldız (Three.js `Points`)
- NASA Blue Marble (2.4 MB) ve NASA Black Marble 2016 şehir ışıkları (7.7 MB) HD dokular
- Küre'den şehir kartlarına animasyonlu SVG konektör çizgileri (dash-flow)

### Zaman Morphing
- Tek `t` parametresi (0.0–1.0) lineer olarak 1800–2026 yıllarına eşlenir
- Klavye: `←/→` = 1 yıl, `Shift+←/→` = 10 yıl, `Space` = oynat/duraklat
- Otomatik oynatma 180 ms/yıl hızında (~40 sn tam yolculuk)

### 7 Dönem Renk Sistemi
| Dönem | Yıllar | Renk |
|-------|--------|------|
| Taş/Barok | < 1870 | Kahverengi |
| Gründerzeit | 1870–1918 | Tan |
| Art Deco | 1918–1945 | Altın |
| Brutalizm | 1945–1965 | Kurşuni |
| Prefabrik | 1965–1980 | Peru |
| Cam & Çelik | 1980–2000 | Çelik Mavisi |
| Modern | ≥ 2000 | Yeşil |

### Gece / Gündüz Modu
- Sıcak gündüz ↔ serin gece, 800 ms CSS geçişiyle
- Three.js küre NASA dokusunu değiştirir; deck.gl ışıklandırması senkronize

### Çok Şehirli
- 11 şehir: New York, Paris, Viyana, Chicago, Berlin, Moskova, Londra, Barselona, Madrid, Tokyo, İstanbul
- Şehir başına lazy GeoJSON fetch; modül düzeyinde cache (yeniden fetch yok)
- Şehre özel renk kimliği ve küre kartı

### Ses Motoru
- Web Audio API native crossfade dönem MP3'leri arasında (1.5 sn linearRamp)
- Frekans visualizer: AnalyserNode (fftSize=128) → Canvas 32 çubuk spektrum

### Tarihsel Olaylar
- Zaman çizelgesinde olay işaretleri (pozitif / negatif / nötr)
- Tıkla → glassmorphism popup + Wikipedia bağlantısı

---

## ML Capstone

> Araştırma sorusu: *Bina inşa dönemi geometrik footprint özelliklerinden ve kentsel bağlamdan tahmin edilebilir mi?*

### Veri (ML-1)

6 açık veri kaynağından **43.500 etiketli bina**:

| Kaynak | Şehir | Bina | Kapsam |
|--------|-------|------|--------|
| NYC PLUTO | New York | 6.453 | %98 |
| ADEME DPE | Paris | 13.334 | %97 |
| Wien Bauperiode WFS | Viyana | 13.872 | %76 |
| Chicago Building Permits API | Chicago | 4.275 | %94 |
| Berlin Geoportal | Berlin | 2.949 | %10 |
| OSM start_date + Overpass | Tüm şehirler | ~2.700 | kısmi |

GHSL (Global Human Settlement Layer, JRC) — 5 epoch 1975–2020, 55 GeoTIFF tile — `ghsl_neighborhood_year` **girdi özelliği** olarak kullanıldı (mahalle kentleşme epochu), inşa yılı etiketi olarak değil.

### Özellikler (ML-2)

Bina başına 14 özellik:

| Özellik | Açıklama |
|---------|---------|
| `area_m2`, `perimeter_m` | Footprint boyutu (Web Mercator) |
| `compactness` | 4π·alan/çevre² |
| `aspect_ratio` | Sınırlayıcı kutu uzunluğu |
| `n_vertices` | Şekil karmaşıklığı |
| `height` | Bina yüksekliği metre cinsinden |
| `dist_to_center_km` | Şehir merkezinden Haversine mesafesi |
| `ghsl_neighborhood_year` | GHSL ilk kentleşme epochu |
| `neighbor_mean_height` | 50 en yakın komşunun ortalama yüksekliği |
| `building_density_200m` | 200 m yarıçap içindeki bina sayısı |
| `lat`, `lon` | Centroid koordinatları |

### Sonuçlar

| Model | Şehir içi CV F1 | Çapraz şehir F1 |
|-------|----------------|----------------|
| XGBoost (n=500, depth=6) | **0.561** ± 0.009 | 0.057 |
| PyTorch MLP (4 katman, CUDA) | 0.469 | 0.089 |

**Temel bulgular:**
- Coğrafi koordinatlar özellik öneminin **%58'ini** oluşturuyor — şehir içi sinyal güçlü ama aktarılamaz
- Footprint şekil özellikleri (compactness, aspect_ratio, n_vertices, alan) **sıfır önem** — şekil dönemi kodlamıyor
- Gerçek sinyal: **yükseklik + komşu yüksekliği + bina yoğunluğu** (kentsel morfoloji)
- Alan adaptasyonu olmadan çapraz şehir transferi başarısız — akademik katkı olarak belgelendi

---

## Teknoloji Stack'i

| Katman | Teknoloji | Sürüm |
|--------|-----------|-------|
| Frontend framework | React | 19 |
| Build aracı | Vite | 5.4 |
| Dil | TypeScript | 5.6 |
| 3D harita motoru | deck.gl | 9.0 |
| 3D küre | Three.js | 0.169 |
| State yönetimi | Zustand | 5.0 |
| Animasyon | Framer Motion | 11 |
| Backend | FastAPI | 0.138 |
| ML | XGBoost 3.2 + PyTorch 2.12 (CUDA) | — |
| Uzamsal | GeoPandas, pyproj, scikit-learn | — |

---

## Hızlı Başlangıç

```bash
# 1. Klonla
git clone https://github.com/minniesmick/chronocity.git
cd chronocity

# 2. Frontend
npm install
npm run dev
# → http://localhost:5173

# 3. Backend (ayrı terminal)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

> ML modeli (`era_model.pkl`) git'e commit edilmez (büyük binary).
> Oluşturmak için: `python ml/train_model.py --model xgb`

---

## ML Kurulumu

Zenginleştirilmiş `buildings.geojson` dosyaları (repoda mevcut) ve GHSL rasterları (`D:/PROJELER/ghsl_raw/`) gerekir.

```bash
cd backend

# 1. Özellik mühendisliği — 14 özellik çıkarır, KNN komşuluk istatistikleri hesaplar
python ml/feature_engineering.py

# 2. XGBoost + PyTorch MLP eğit
python ml/train_model.py --model both

# 3. API başlat
uvicorn main:app --port 8000
```

---

## API Referansı

### `GET /api/health`
```json
{ "status": "ok", "service": "chronocity" }
```

### `POST /api/predict-era`
Tek bina için dönem tahmini.

```json
// İstek
{
  "city": "vienna",
  "lon": 16.370, "lat": 48.208,
  "height": 18.0,
  "area_m2": 600, "building_density_200m": 15
}

// Yanıt
{
  "era": 1,
  "era_name": "Gründerzeit",
  "era_period": "1870–1918",
  "era_color": "#C19A6B",
  "confidence": 0.590
}
```

### `POST /api/predict-era/batch`
1000 binaya kadar toplu tahmin.

### `GET /api/predict-city/{city}?limit=5000`
Bir şehrin tüm etiketsiz binaları için tahmin.

---

## Proje Yapısı

```
chronocity/
├── backend/
│   ├── main.py                   # FastAPI: health + predict-era + predict-city
│   ├── predict_era.py            # Model yükleme + çıkarım yardımcıları
│   └── ml/
│       ├── enrich_buildings.py   # ML-1: veri zenginleştirme
│       ├── feature_engineering.py # ML-2: 14 özellik, BallTree KNN
│       ├── train_model.py        # ML-2: XGBoost + PyTorch eğitim
│       └── download_ghsl.py      # GHSL toplu indirici
├── public/
│   ├── cities/{şehir}/
│   │   ├── buildings.geojson     # height + construction_year + data_source
│   │   ├── events/info.json
│   │   └── music/{dönem}.mp3
│   └── textures/
│       ├── earth-day.jpg         # NASA Blue Marble HD (2.4 MB)
│       └── earth-night.jpg       # NASA Black Marble 2016 (7.7 MB)
├── scripts/
│   └── enrich_years_catastro.py  # İspanya Katastrosu ile inşa yılı zenginleştirme
├── src/
│   ├── components/
│   │   ├── GlobeSelector.tsx     # Three.js küre + galaksi giriş animasyonu
│   │   ├── MapCanvas.tsx         # deck.gl 3D çekirdek
│   │   ├── TimelineBar.tsx
│   │   ├── BuildingPopup.tsx
│   │   └── EraAudioEngine.tsx
│   ├── data/cities.ts            # 11 şehir kaydı
│   ├── lib/
│   │   ├── buildingColors.ts     # 7 dönem renk sistemi
│   │   └── time.ts
│   └── store/useStore.ts
├── UX_advice.md                  # UX gözlemleri ve öneriler
└── package.json
```

---

## Yol Haritası

- [x] S0 — Scaffold: React 19 + Vite + TS + Zustand + FastAPI + design token'lar
- [x] S1 — 3D çekirdek: deck.gl binalar, time morph (1800–2026), gece/gündüz toggle, dönem renkleri
- [x] S2 — Küre: Three.js küre seçici, sinematik giriş, şehir yükleme ekranı, React Router
- [x] S3 — Zaman çizelgesi: scrubber bar, olay işaretleri, olay popup'ları, replay butonu
- [x] S4 — Ses: dönem MP3 crossfade (Web Audio API), frekans visualizer
- [x] S5 — Çok şehir: 11 şehir, lazy data loader, fly-to animasyonu, bina popup
- [x] S6 — Görsel cila: NASA HD dokular, galaksi giriş, yıldız alanı, vignette, konektör animasyonları
- [x] ML-1 — Veri: 43.500 etiketli bina, 6 açık veri kaynağı, GHSL komşuluk özelliği
- [x] ML-2 — Model: XGBoost (CV F1=0.561) + PyTorch MLP (CUDA), çapraz şehir değerlendirme
- [x] ML-3 — API: `/api/predict-era`, `/api/predict-era/batch`, `/api/predict-city/{city}`
- [ ] ML-4 — Frontend: köken rozetleri (PLUTO/OSM/AI), AI tahminli bina görselleri, filtre paneli
- [ ] S10 — QA: cross-browser, Lighthouse, jüri demo scripti, teknik rapor

---

## Yazar

**Alper Yusuf Yaman**
[@minniesmick](https://github.com/minniesmick) on GitHub

---

## Lisans

[MIT Lisansı](./LICENSE) altında lisanslanmıştır.

© 2026 Alper Yusuf Yaman.

---

<div align="center">
  <sub>Şehirler her şeyi hatırlar. ChronoCity, onlarla birlikte hatırlamanı sağlar.</sub>
  <br/><br/>
  <a href="#top">↑ en başa dön</a>
</div>
