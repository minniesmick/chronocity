# ChronoCity — Fable Advice
*Kod tabanının satır satır taranmasıyla çıkarılmış tavsiyeler. Her madde dosya:satır kanıtlı.*
*Efor: (S) < 1 saat · (M) yarım gün · (L) 1+ gün. Etki: ★–★★★*

---

## BÖLÜM 1 — NOT ODAKLI (jüri bunu puanlıyor)

### 1.1 ⚠️ EN KRİTİK BULGU: Backend görünmez durumda

`backend/main.py` 11 endpoint sunuyor — NLP arama, şehir istatistikleri, AI insights,
city assistant, tekil/batch/şehir-geneli era tahmini, WebSocket. `era_model_xgb.json`
18MB eğitilmiş XGBoost. `vite.config.ts` proxy'si hazır (`/api` → :8000).

**Frontend'de tek bir `/api` çağrısı yok.** Grep kanıtı: `src/` altında yalnız üç fetch var,
üçü de statik dosyaya gidiyor (`useCityBuildings.ts:45`, `useCityEvents.ts:11`,
`useEraAudio.ts:54`).

Jüri frontend'i görür. Capstone'un ML çekirdeği şu an demo edilemez durumda.
Aşağıdaki 1.2–1.6 bu boşluğu kapatma planı — hepsi backend'de hazır, sadece UI bağlantısı eksik.

### 1.2 NLP arama çubuğu → bina highlight (M, ★★★)

`POST /api/cities/{id}/search` zaten `matched_ids` + insan-dili `answer` dönüyor
(`main.py:84-116`). Demo anı: jüri önünde `"show tall buildings before 1930"` yaz,
haritada eşleşen binalar parlasın.

Uygulama:
- `city-exp__top`'a arama input'u (mevcut glass stil, `sprint1.css` pill dili).
- Dönen `matched_ids`'i `Set`'e koy; `MapCanvas.tsx` GeoJsonLayer `getFillColor`'da
  `matchedSet.has(f.properties.id)` ise parlak renk, değilse mevcut era rengi soluk.
  `updateTriggers.getFillColor`'a `searchResultsVersion` ekle (Set referansı değil —
  sayaç arttır, gereksiz derin karşılaştırma olmaz).
- `answer` string'ini arama kutusunun altında göster ("42 buildings match…").
- `GET /suggestions` (`main.py:129`) → input focus'ta hazır öneri chip'leri; jüri
  yazmak zorunda kalmaz, tıklar.

### 1.3 AI era tahmini katmanı (M, ★★★)

`GET /api/predict-city/{city}` tahmin + `confidence` + `era_distribution` dönüyor
(`main.py:224-296`). UI'da "AI Tahmin" toggle'ı:

- Açılınca: `construction_year == null` binalara `predicted_era_color` bas.
- `confidence`'ı alpha'ya bağla (0.5 → soluk, 0.95 → tam renk) — akademik dürüstlük
  görsel dile dönüşür, jüri sorusu gelmeden cevaplanmış olur.
- `era_distribution` response'ta hazır → bottom HUD'a mini histogram (bkz. 1.5).

**Önce şu bug'ı düzelt:** `main.py:237` `predict.parquet` yolu hardcode:
`D:\PROJELER\ml_data\predict.parquet`. Demo başka makinede/diskte çalışırsa 404.
`os.environ.get("CHRONO_ML_DATA", ...)` + `.env.example` dosyası. (S ama demo sigortası)

### 1.4 BuildingPopup provenance + confidence rozeti (S-M, ★★★)

`BuildingPopup.tsx` şu an yıl/yükseklik gösteriyor. Ekle:
- Kaynak rozeti: `PLUTO` / `OSM` / `MS Footprints` / `AI tahmin` — enrich pipeline'ının
  yazdığı source alanı properties'te varsa direkt, yoksa `enrich_buildings.py`'a ekletmek
  yarım günlük iş.
- AI tahminliyse: `~1970s · %78 güven` formatı. "Bilinmiyor" yerine model devreye girer —
  capstone anlatısının kalbi bu popup'ta görünür olur.

### 1.5 Era histogram — data science tek bakışta (M, ★★)

`GET /api/cities/{id}/stats` (`city_analytics.py`) dönem dağılımını zaten hesaplıyor.
Bottom HUD'a veya toggle panele bina/dönem bar chart. Timeline oynarken güncel yıla
kadar olan kısım doluyor gibi animasyon = "veri + zaman" hikayesi tek görselde.
SVG ile elle çiz (recharts ekleme — bundle şişer, 7 bar için gerek yok).

### 1.6 City Assistant drawer (M, ★★ — vakit kalırsa)

`POST /ask` rule-based cevap üretiyor (`main.py:140-152`), LLM'siz bile çalışıyor.
Sağ kenardan açılan chat drawer; jüriye "buraya sonra Gemini bağlanabilir" mimari
vizyonu anlatılır. Düşük risk: backend cevabı deterministik.

### 1.7 Metodoloji modal'ı — "veri nereden?" sorusunun cevabı UI'da (S-M, ★★★)

Jürinin garanti sorusu. Şu an cevap dağınık: `references.md`'ler diskte (9 şehir,
UI'da görünmüyor), veri kaynakları README'de. Tek "ⓘ Metodoloji" modal'ı:
- Veri: PLUTO, Microsoft Building Footprints, OSM, GHSL, NASA Blue/Black Marble
- Model: XGBoost, feature listesi (`feature_engineering.py`'dan), sınırlamalar
- Events kaynakçaları: her şehrin `references.md`'sine link/accordion
Akademik ciddiyet + savunma hazırlığı tek yerde.

### 1.8 EventPopup Wikipedia linki yanlış dile gidiyor (S, ★★)

`EventPopup.tsx:49`: `https://tr.wikipedia.org/wiki/${ev.wikiSlug}` — ama 9 şehrin
events'i artık akademik İngilizce, slug'lar EN Wikipedia'dan. TR Wikipedia'da çoğu
slug 404 verir. Jüri tıklarsa kötü görüntü. `en.wikipedia.org`'a çevir; ideali 1.7'deki
kaynakça yaklaşımıyla değiştirmek.

### 1.9 Berlin + İstanbul events hâlâ Türkçe (S, ★★)

9 şehir İngilizce APA'lı, bu ikisi Türkçe — jüri iki şehirden birine tıklarsa dil kırılması.
Aynı formatta çevir (`public/cities/{berlin,istanbul}/events/info.json` + `references.md`).

### 1.10 URL deep-link — demo script sigortası (S, ★★)

`/city/new-york?year=1931` → `t` store'unu URL param ile senkronla
(`useSearchParams`, sadece okuma mount'ta + debounced yazma). Demo script'i
"Empire State yılına atla" tek tıkla; canlı demo'da slider'la uğraşma riski sıfırlanır.

### 1.11 Ucuz mühendislik puanları (S-M, ★)

- `package.json:4` version `0.1.0` ama README badge `0.3.0` — senkronla.
- Vitest + 10-15 unit test: `lib/time.ts` (yearFromT/tFromYear roundtrip),
  `lib/buildingColors.ts` (band sınırları), backend `nlp_search.parse_query`
  (pytest). Jüri rubriğinde "test" satırı varsa boş kalmasın.
- GitHub Actions: lint + build + test badge README'ye.
- `CityExperience.tsx:50-53`: `navigate()` render gövdesinde — React anti-pattern
  (StrictMode uyarısı). `useEffect`'e taşı.

---

## BÖLÜM 2 — PERFORMANS

### 2.1 🔥 En büyük sorun: 20fps pulse tüm şehri yeniden boyuyor

Zincir şu (`MapCanvas.tsx:57-70, 195`):
1. `frame` state 50ms'de bir artıyor (20fps).
2. `updateTriggers.getFillColor: [currentYear, isDayMode, frame]` → **her 50ms'de
   170K binanın fill color attribute'u CPU'da yeniden hesaplanıp GPU'ya yükleniyor.**
3. Üstüne `transitions: { getFillColor: 400 }` → her tetiklemede 400ms interpolasyon —
   animasyon hiç bitmiyor, sürekli attribute güncelleme.

Tek amaç: `colorUndated`'daki nefes efekti (`buildingColors.ts:33-38`) — yalnız
`construction_year == null` binalar için.

**Çözüm: katmanı ikiye böl.**
```ts
// data'yı bir kez ayır (useMemo, data değişince):
const { dated, undated } = useMemo(() => splitByYear(data), [data]);

// Katman 1 — dated: frame YOK, transitions kalabilir
new GeoJsonLayer({ id: `bld-dated-${city}`, data: dated,
  updateTriggers: { getElevation: currentYear,
                    getFillColor: [currentYear, isDayMode] } })

// Katman 2 — undated: pulse'ı attribute'la değil LAYER OPACITY ile yap
new GeoJsonLayer({ id: `bld-undated-${city}`, data: undated,
  getFillColor: night ? [50,60,80,200] : [95,105,125,200], // SABİT
  opacity: 0.35 + 0.25 * Math.sin(frame * 0.08),           // uniform — bedava
  updateTriggers: { getElevation: currentYear } })
```
`opacity` layer-level uniform: attribute recompute YOK, GPU'ya tek float gidiyor.
`frame` artık hiçbir updateTrigger'da değil. Tokyo/Moscow gibi undated-ağır şehirlerde
kare hızı gözle görülür düzelir. **(M, ★★★)**

Bonus: `frame` state yerine `useRef` + deck.gl'in kendi `onAnimationFrame`'i ile
opacity'yi imperative set etmek React re-render'ını da bitirir — ama önce yukarıdaki
bölme yapılsın, yeterli gelebilir.

### 2.2 GeoJSON boyutları: 71MB toplam, en büyüğü 12.7MB (M, ★★★)

`public/cities/*/buildings.geojson`: 12.7 / 10.4 / 8.9 / 8.3 / 7.7 / 6.6 / 6.1 MB…
Localhost'ta maskeleniyor; herhangi bir deploy'da (jüri "linki açın" derse) felaket.

Sıralı reçete:
1. **Koordinat hassasiyeti düşür** (script, tek seferlik): GeoJSON'lar muhtemelen
   7+ ondalık taşıyor. 6 hane = 11cm hassasiyet, bina için fazlasıyla yeter.
   `python -c "..."` ile truncate → %25-40 küçülme, görsel fark sıfır.
2. **Properties diyeti**: her feature'da kullanılmayan alan var mı bak
   (`enrich_buildings.py` ne yazıyor?). Frontend yalnız `height`,
   `construction_year`, `name`, `id`, source kullanıyor. Gerisi at.
3. **Brotli precompress**: `vite-plugin-compression2` ile build'de `.br` + `.gz` üret;
   GeoJSON %85-92 sıkışır → 12.7MB ≈ 1.3MB tel üstünde. Host static-precompressed
   servis edecek şekilde ayarla (Netlify/Vercel otomatik, nginx `gzip_static`).
4. (Uzun vade, L) Binary format — flatgeobuf/GeoArrow. Capstone için 1-3 yeter.

### 2.3 Route-level code splitting (S-M, ★★★)

`App.tsx` üç route'u da eager import ediyor. Three.js (~600KB min) yalnız globe'da,
deck.gl (~1MB+ min) yalnız city'de gerekli. Intro ikisini de kullanmıyor ama kullanıcı
ikisinin de parse bedelini intro'da ödüyor.

```tsx
const GlobeSelector  = lazy(() => import("@/components/GlobeSelector"));
const CityExperience = lazy(() => import("@/components/CityExperience"));
// Routes'u <Suspense fallback={<düz siyah div>}> ile sar
```
Not: `AnimatePresence mode="wait"` + lazy kombinasyonunda exit animasyonu için
fallback'i boş/siyah tut — mevcut fade zaten karanlığa gidiyor, kesinti hissedilmez.
İlk boyama süresi ciddi düşer; Lighthouse (S10) puanına direkt yazar.

### 2.4 Globe texture stratejisi (S, ★★)

`public/textures/`: `earth-night.jpg` **7.7MB**, `earth-day.jpg` 2.4MB — ve diskte
duran ama hiç kullanılmayan `earth-night-2048.jpg` (0.6MB).

Globe ekranda ~500-900px. 8K gece dokusu overkill:
- Hızlı yol: geceyi 4096'ya resize (~2MB), günü bırak.
- Şık yol (progressive): önce `earth-night-2048.jpg`'yi yükle (intro zoom'u sırasında
  globe asla çıplak kalmaz), arkada full-res fetch edip `applyTex` ile değiştir.
  `GlobeSelector.tsx:203-211`'deki loader zinciri buna hazır — iki `loader.load`
  çağrısını zincirle.

### 2.5 Google Fonts render-blocking + demo venue riski (S, ★★)

`index.html:9-14`: Space Grotesk + Inter CDN `<link>` ile. İki risk: render-blocking
CSS, ve jüri salonunda internet yavaşsa/yoksa sistem fontuna düşme (tasarım kimliği
gider). `@fontsource/space-grotesk` + `@fontsource/inter` (woff2 self-host, subset
latin+latin-ext) → hem offline-güvenli hem hızlı.

### 2.6 Ölü bağımlılıklar (S, ★)

`package.json`'da import edilmeyen dört paket: `tone`, `gsap`, `maplibre-gl`,
`react-map-gl` (grep: sıfır import; audio raw Web Audio API ile yazılmış —
`lib/audioContext.ts`). Bundle'a girmiyorlar (tree-shake) ama `npm install` süresi,
güvenlik yüzeyi ve "neden duruyor?" sorusu için: `npm uninstall tone gsap maplibre-gl react-map-gl`.
README_Tr zaten "Tone.js yok" diyor — package.json'ı söze uydur.

### 2.7 Küçük perf borçları (S, ★)

- `onViewStateChange` her frame `setCurrentZoom` çağırıyor (`MapCanvas.tsx:213`) —
  zustand üzerinden `EraLegend` zoom göstergesi pan/zoom sırasında 60fps re-render.
  Store yazımını `Math.round(z*10)/10` değişmediyse atla.
- `useCityEvents` cache'siz — şehre her girişte refetch (`useCityEvents.ts:11`).
  `useCityBuildings`'teki module-cache desenini kopyala.
- `GlobeSelector` cleanup'ında globe/atmosfer/grid geometry+material dispose
  edilmiyor (yalnız star/mw ediliyor, `GlobeSelector.tsx:429-434`). Globe↔city
  gidiş-gelişlerinde GPU bellek sızar. Scene traverse edip dispose et.

---

## BÖLÜM 3 — KOZMETİK

### 3.1 ⚠️ Müzik: UI var, dosya yok (S — karar meselesi, ★★★)

`public/cities/**/music/` altında **0 adet mp3**. Ama TimelineBar era pill'leri
("60'lar / 80'ler / 2000'ler / Modern") tıklanabilir duruyor, `useEraAudio` sessizce
404 yutuyor (`useEraAudio.ts:82` `catch(() => {})`), `FrequencyVisualizer` boş analyser
çiziyor. Jüri pill'e tıklar → hiçbir şey olmaz → "kırık" izlenimi. İki yol:

- **A (önerilen, hızlı):** Müzik gelene kadar era pill'lerini ve FrequencyVisualizer'ı
  feature flag'le gizle. Kırık görünen özellik, olmayan özellikten kötüdür.
- **B (tam çözüm):** Şehir başına değil, era başına 4 telifsiz parça bul
  (Musopen/Free Music Archive, CC0) → `music/` klasörüne koy; `useEraAudio`
  şehir yolunu era-fallback'li yap. Site kimliğinin "her dönemin sesini duy" vaadi
  (index.html description!) gerçekleşir.

### 3.2 Dil tutarlılığı: TR chrome + EN içerik (M, ★★)

UI Türkçe ("geri", "Durdur", "NÜFUS", "binalar yükleniyor…"), events akademik İngilizce,
`index.html` `lang="tr"`. Karışım profesyonel durmuyor. Basit dictionary i18n
(`src/lib/i18n.ts`, ~40 string, TR/EN toggle top bar'a) hem tutarlılık hem "+1 feature".
Jüri Türkçe sunumda TR, raporda EN ekran görüntüsü alabilirsin.

### 3.3 UX_advice kalanları — hâlâ geçerli olanlar

- **4C** EraLegend + TimelineBar + Replay tek glass panelde (S-M, ★) — bottom HUD'da
  üç ayrı görsel dil var; tek `border-glass` konteynır sakinleştirir.
- **4F** `hasBuildingData: false` şehir kartlarına "veri yakında" satırı (S, ★) —
  şu an detail bölümü boş açılıyor.
- **4G** Globe gündüz/gece texture crossfade (M, ★) — anlık swap yerine iki mesh
  300ms opacity geçişi. Cilalı ama acil değil.
- **4H** Mobil FOV 36→28 veya kamera z 5.8 (S, ★) — jüri demosu telefondan
  olmayacaksa erteleyebilirsin.
- **4D** Shortcut overlay'i tam ekran yerine sağ-alt kart (S, ★).

### 3.4 Fly-to animasyonu `prefers-reduced-motion`'ı bilmiyor (S, ★)

Dün eklenen 1G kamera uçuşu (`GlobeSelector.tsx` RAF bloğu) JS-driven —
`sprint2.css`'teki global reduced-motion kuralı onu yakalamaz.
`matchMedia("(prefers-reduced-motion: reduce)").matches` ise `flyToRef` set etmeden
direkt `navigate()`. Erişilebilirlik rubriği varsa ucuz puan.

### 3.5 Loading yüzdesi gerçek veriye bağlansın (S-M, ★)

`MapCanvas.tsx:244` "binalar yükleniyor…" statik. 12.7MB'lık şehirde bu uzun sürüyor.
`fetch` + `Content-Length` + ReadableStream ile gerçek % göster; CityLoadingScreen
bar'ı zaten var (`city-loading__bar-fill`) — sahte timer yerine gerçek indirme
yüzdesine bağla. "Yükleniyor hissi" premium'laşır.

### 3.6 Mikro dokunuşlar (S, ★)

- `TimelineBar.tsx:95` play butonu `⏸`/`▶` text glyph — projedeki `PlayerIcon`
  ikon setiyle değiştir (tek ikon ailesi kuralı).
- `MapCanvas.tsx:234-235` zoom hint `⊖`/`⊕` — aynı şekilde.
- `timeline__era-pill` `title` attribute'u dev yolu gösteriyor
  (`/public/cities/{şehir}/music/...`, `TimelineBar.tsx:163`) — kullanıcıya iç yol
  sızdırma, kaldır.
- `city-year-bg` dekoratif yıl sağda sabit — Empire State gibi sağ-ağırlıklı
  şehirlerde binalarla çakışabilir; `mix-blend-mode: overlay` + opacity düşürme
  dene, daha "müze" durur.

---

## ÖNERİLEN SIRA (2 haftalık sprint kurgusu)

| Gün | İş | Bölüm |
|-----|-----|-------|
| 1 | 2.1 katman bölme + 2.6 dep temizliği + 1.3'teki path fix | Perf + sigorta |
| 2 | 2.3 code splitting + 2.4 texture + 2.5 font self-host | Perf |
| 3-4 | 1.2 NLP arama + highlight | **NOT** |
| 5-6 | 1.3 AI tahmin toggle + confidence alpha | **NOT** |
| 7 | 1.4 BuildingPopup provenance + 1.8 wiki link + 1.9 Berlin/İstanbul EN | NOT |
| 8 | 1.5 era histogram + 1.7 metodoloji modal | NOT |
| 9 | 2.2 GeoJSON diyet + brotli | Perf |
| 10 | 3.1 müzik kararı + 3.2 i18n | Kozmetik |
| 11 | 1.10 deep-link + 1.11 testler/CI | NOT |
| 12 | S10: Lighthouse, cross-browser, demo script provası | — |

**Tek cümlelik özet:** Capstone'un ML kalbi backend'de atıyor ama vitrine çıkmamış —
önce onu bağla (1.2–1.5), sonra 20fps pulse'ı söndür (2.1), gerisi cila.

*Yazan: Claude (Fable 5) — 2026-07-11*
