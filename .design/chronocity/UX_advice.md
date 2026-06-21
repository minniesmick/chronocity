# ChronoCity — UX Tavsiye Raporu
> `/impeccable` skill çıktısı — product register, dark-tech-cinematic aesthetic  
> İki ekran incelendi: Globe + City. Öncelik sırasıyla gruplanmıştır.

---

## 🔴 KRİTİK — Demo öncesi düzeltilmesi gereken

### 1. Bina vs Satellite Uyumsuzluğu (Gündüz Modu)

**Problem:** Gündüz modunda satellite opacity = 1.0. NASA/ESRI fotoğrafik zemin
çok canlı (yeşil parklar, gri yollar, mavi göl). Üstündeki era-renkli binalar
`material.ambient: 0.5` + `material.diffuse: 0.6` ile **deck.gl'in
aydınlatma formülünden geçince ~%40 karardığından** satellite'tan daha koyu
çıkıyor. Sonuç: binalar fotoğrafın üstünde yüzen siluet gibi görünüyor.

**Neden bu oluyor:**
- `colorByEra` day mode `mul = 1.0` → max RGB ~200 → orta ton
- deck.gl `ambient * ambientIntensity + diffuse * diffuseIntensity * cos(angle)` formülü ≈ 0.5×1.1 + 0.6×1.4×0.6 ≈ 1.05 → ancak yüzey normaline göre değişir, gölgeli yüzler %40-60 altına düşer
- `alpha: 220` (86%) → kenarlardan satellite bleeding
- Undated binalar `[95,105,125]` = koyu mavi-gri → çok dark

**Düzeltmeler (sırasıyla uygula, test et):**

```typescript
// 1. MapCanvas.tsx — satellite opacity gündüzde 1.0 → 0.80
opacity: isDayMode ? 0.80 : 0.45,

// 2. buildingColors.ts — gündüz era çarpanı 1.0 → 1.25
const mul = night ? 0.55 : 1.25;   // 200 × 1.25 = 250, üst sınırı Math.min(255,…) ile kır

// 3. MapCanvas.tsx material — ambient 0.5 → 0.72 (gölgeli yüzler daha az karar)
material: {
  ambient: 0.72,    // was 0.5
  diffuse: 0.45,    // was 0.6 (daha az directional gölge)
  shininess: 32,
  specularColor: [60, 50, 40],
},

// 4. GeoJsonLayer — ince bina kenarı kontur (satellite'tan ayırır)
getLineColor: (f: BFeature) =>
  isBuilt(f, currentYear) ? [255, 255, 255, 25] : [0, 0, 0, 0],
stroked: true,
lineWidthMinPixels: 0.5,
```

Öncelik: 1+3 → ikisi birlikte gece/gündüz dengesini korur. 2+4 ekstra.

---

### 2. `--font-mono` Token Yanlış Font'u Gösteriyor

**Problem:** `tokens.css`'de:
```css
--font-mono: "Space Grotesk", ui-monospace, "Cascadia Code", monospace;
```
Space Grotesk bir **variable sans-serif**tir, monospace değil. Tarayıcı ilk
font'u yüklenmiş bulursa onu kullanır. Sonuç: zoom level (`12.2 ×`), era
legend periyotları (`1870–1918`), timeline tick'leri — hepsi orantılı font ile
render oluyor. Rakamlar değişken genişlikte. Tablolar hizalanmaz.

**Düzeltme:**
```css
--font-mono: "JetBrains Mono", "Cascadia Code", ui-monospace, monospace;
```
`package.json`'a font package ekle ya da `@font-face` ile local serve et.
Alternatif: `font-variant-numeric: tabular-nums` + Space Grotesk (gerçek mono
değil ama sayı hizalaması düzelir).

---

### 3. Timeline Play/Pause Emoji Kullanıyor

**Problem:** `timeline__play` butonu `⏸` / `▶` emoji. Farklı OS/tarayıcıda
farklı render eder (Windows emoji seti vs macOS vs Linux). Proje'nin kendi
ikon sistemi var (`PlayerIcon`, `RefreshIcon`).

**Düzeltme:**
```tsx
// TimelineBar.tsx
import PlayerIcon from "@/components/icons/player-icon";
// …
<button className="timeline__play" onClick={…}>
  {isPlaying
    ? <span className="timeline__pause-bars">▐▐</span>  // veya inline SVG
    : <PlayerIcon size={14} color="currentColor" />
  }
</button>
```
Ya da iki dikey çizgi `||` bir `<span>` içinde CSS'le şekillendir.

---

## 🟠 YÜKSEK ÖNCELİK

### 4. Globe Ekranında Ürün Kimliği Yok

**Problem:** Globe açılıyor, dönen küre var, ama "ChronoCity" adı ya da ne
olduğuna dair hiçbir ipucu yok. Jüri/ziyaretçi ilk 10 saniyede anlamak
zorunda. Şu an tek context `"Sürükle · Döndür · Bir şehre tıkla"` hint'i.

**Düzeltme:** Sol üst köşeye compact wordmark:
```tsx
<div className="globe-wordmark">
  <span className="globe-wordmark__name">CHRONO</span>
  <span className="globe-wordmark__accent">CITY</span>
</div>
```
```css
.globe-wordmark {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  z-index: 10;
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--color-text);
  animation: fade-in 1.2s ease both;
}
.globe-wordmark__accent { color: var(--color-accent); }
```

---

### 5. Kamera Sıfırlama Butonu Yok

**Problem:** Kullanıcı haritayı döndürüp/zoom yaptıktan sonra başlangıç
görünümüne (zoom 14.5, pitch 50, bearing -20) dönmenin yolu yok. ReplayButton
yalnızca zaman çizelgesini sıfırlıyor.

**Düzeltme:** `MapCanvas`'a `resetCamera` fonksiyonu, `CityExperience`'ta
prop'a aç, üst bar'a küçük LocateIcon butonu:
```tsx
// MapCanvas.tsx
const resetCamera = () => {
  setViewState({
    longitude: center[0], latitude: center[1],
    zoom: 14.5, pitch: 50, bearing: -20,
    minZoom: 12, maxPitch: 75,
    transitionDuration: 900,
    transitionInterpolator: new FlyToInterpolator({ speed: 1.6 }),
  });
};
```
```tsx
// CityExperience.tsx header'a ekle:
<LocateIcon size={14} /> <button onClick={resetCamera}>Merkez</button>
```

---

### 6. Keyboard Shortcuts Görünmez

**Problem:** `←/→` = 1 yıl, `Shift+←/→` = 10 yıl, `Space` = play/pause
kodlanmış ama kullanıcıya hiçbir yerde gösterilmiyor. Demo'da jüri tıklamakla
uğraşırken sen "Space'e bas" diyeceksin.

**Düzeltme:**
- Timeline'da `?` ikonu → hover'da küçük shortcut tooltip
- Ya da timeline `__ticks` altına tek satır: `SPACE oynat · ← / → yıl`
- CSS: `font-mono 10px`, `color-text-faint`, `pointer-events:none`

---

### 7. Building Popup — Null Year için Empty State Yok

**Problem:** `BuildingPopup`, `construction_year: null` olan binalarda
boş/hatalı veri gösterebilir. `eraByYear(null)` nasıl handle ediyor kontrol
edilmeli.

**Düzeltme:** Popup içinde:
```tsx
{p.construction_year
  ? <span>{p.construction_year} · {era.label}</span>
  : <span className="bpop__unknown">Yapım yılı bilinmiyor</span>
}
```
Ayrıca `Escape` tuşuyla popup kapatma event listener ekle.

---

### 8. FlyTo Başlangıç Zoom = 5 ama minZoom = 12

**Problem:** `viewState` başlangıçta `zoom: 5` set ediliyor ama `minZoom: 12`
bunu anında 12'ye clamp ediyor. "Uzaydan yaklaşma" efekti kayboluyor. Kullanıcı
şehire geldiğinde zoom 12'den 14.5'e kısa bir fly görüyor.

**Seçenekler:**
- A) İlk viewState zoom'unu 12'de başlat, FlyTo daha dramatik pitch+bearing
  değişimi ile aynı "sinematik giriş" hissini ver.
- B) `minZoom`'u FlyTo tamamlandıktan sonra set et:
  ```tsx
  // FlyTo tamamlanınca minZoom set et
  onViewStateChange={({ viewState: vs }) => {
    const newVs = vs as MapViewState;
    if (newVs.zoom > 13.5 && !minZoomLocked.current) {
      minZoomLocked.current = true;
      // artık minZoom uygula
    }
  }}
  ```

---

## 🟡 UX POLISH

### 9. Timeline Track — Era Renk Bantları Yok

**Problem:** Timeline track düz dolgu çizgi. Çizelgedeki 226 yılın dönemlere
bölündüğünü göstermiyor. Jüri "neden binalar bu renkte?" sorusunu sorduğunda
görsel yanıt yok.

**Düzeltme:** Track altına `--z-index:0` olarak gradient segment strip:
```css
/* Era bantları: 1800→1870→1918→1945→1970→1990→2010→2026 */
.timeline__era-strip {
  position: absolute;
  left: 0; right: 0;
  bottom: 0;
  height: 3px;
  background: linear-gradient(to right,
    rgb(180,150,100)  0%,     /* taş/barok */
    rgb(180,150,100)  30.5%, /* → 1870 */
    rgb(190,120,80)   30.5%,  /* grunderzeit */
    rgb(190,120,80)   51.3%,
    rgb(200,165,60)   51.3%,  /* art deco */
    rgb(200,165,60)   63.5%,
    rgb(140,150,160)  63.5%,  /* brutalizm */
    rgb(140,150,160)  75.2%,
    rgb(175,175,155)  75.2%,  /* prefab */
    rgb(175,175,155)  83.6%,
    rgb(130,175,150)  83.6%,  /* cam/celik */
    rgb(130,175,150)  92.5%,
    rgb(100,170,215)  92.5%,  /* modern */
    rgb(100,175,215)  100%
  );
  border-radius: 0 0 4px 4px;
  opacity: 0.6;
}
```
Yüzdeler: `(year - 1800) / 226 * 100`.

---

### 10. Sol Alt HUD Kalabalığı

**Problem:** `12.2 ×` (bottom: 140px, left) + `DÖNEMLER ›` (bottom: 160px,
left) üst üste oturuyor. İkisi de sol alt köşeyi dolduruyor, boşluk yetersiz.

**Düzeltme A — Birleştir:** Era legend toggle'ına zoom değerini entegre et:
```tsx
<button className="era-legend__toggle">
  <span className="era-legend__dot-row">…</span>
  <span className="era-legend__label">DÖNEMLER</span>
  <span className="era-legend__zoom">{viewState.zoom?.toFixed(1)} ×</span>
  <span className="era-legend__chevron">›</span>
</button>
```
`map-zoom-level` div'ini kaldır.

**Düzeltme B — Pozisyon:** zoom'u sağ alta, era legend sol alta. Bu iki HUD
elemanı farklı köşelere dağıtır.

---

### 11. Globe Hint Text Asla Kaybolmuyor

**Problem:** `"Sürükle · Döndür · Bir şehre tıkla"` pulse animasyonu sonsuz
çalışıyor. Deneyimli kullanıcıda gürültü.

**Düzeltme:**
```tsx
const [hintVisible, setHintVisible] = useState(true);
// İlk drag ya da 5 saniye sonra gizle
useEffect(() => {
  const t = setTimeout(() => setHintVisible(false), 5000);
  return () => clearTimeout(t);
}, []);
// Canvas'ta pointer down'da da gizle
```
```tsx
<AnimatePresence>
  {hintVisible && (
    <motion.p className="globe-selector__hint" exit={{ opacity: 0 }}>
      Sürükle · Döndür · Bir şehre tıkla
    </motion.p>
  )}
</AnimatePresence>
```

---

### 12. Night Mode Body Transition Yok

**Problem:** Gündüz → Gece geçişinde deck.gl binalar yumuşak geçiyor (400ms
transition) ama `body` arka planı, üst bar background'ları anında değişiyor.
Göz takılma yaratıyor.

**Düzeltme:** Global CSS'te:
```css
.city-exp,
.city-exp__top,
.daynight {
  transition: background var(--duration-slow) var(--ease-standard);
}
```

---

### 13. FrequencyVisualizer Amaçsız Görünüyor

**Problem:** Sağ altta küçük canvas bar grafiği var. Çalışıyor ama neyin
göstergesi olduğu belirtilmemiyor. "Bu ses frekans analizi mi?" "Binaların
istatistiği mi?" belirsiz.

**Düzeltme:** Tek satır label veya tooltip:
```tsx
<div className="freq-viz-wrap" title="Müzik frekans görselleştirici">
  <FrequencyVisualizer />
</div>
```
Ya da era badge'inin yanına entegre et (hangi dönem müziği çaldığını belirt).

---

### 14. HUD Sticky Düzeni — Öneri

Kullanıcının sorusuna cevap: Mevcut `position: absolute` full-screen viewer
içinde doğru yaklaşım. Scroll olmayan ekranda "sticky" ile "absolute" aynı
sonucu verir.

**Şu anki HUD bölgeleri:**
```
┌─────────────────────────────────────────────────┐
│  [geri] [Chicago]          [Gündüz] [Gece]      │  ← TOP BAR (sabit, iyi)
│                                                  │
│           3D HARITA                              │
│                                                  │
│  [DÖNEMLER›]         [FreqViz]                   │  ← MID-LEFT + MID-RIGHT
│  [12.2×]                                         │
│                    [▶ 2026 ━━━━━━━━━]            │  ← BOTTOM-RIGHT (timeline)
└─────────────────────────────────────────────────┘
```

**Öneri:** Timeline'ı full-width bottom'a al, height azalt, sol boşlukta da
play/pause + yıl kalsın. Bu, "harita tam genişlik — kontroller altta" HUD
dilini netleştirir ve era strip (madde 9) için daha geniş alan sağlar.

```
┌─────────────────────────────────────────────────┐
│  [geri] [Chicago]          [Gündüz] [Gece]      │
│                                                  │
│           3D HARITA                              │
│                                                  │
│  [DÖNEMLER›]                         [12.2×]    │
├─────────────────────────────────────────────────┤
│  ▶  2026  ▁▃▅▆▅▃ ━━━━━━━━━━━━━━━━━━━━━━━━━ ↺   │
└─────────────────────────────────────────────────┘
```

---

## 🟢 GÜZEL OLUR (demo sonrası)

### 15. City Stats Sidebar

`CITIES[city].stats` objesi var (`population`, `founded`, `milestones`) ama
hiçbir yerde render edilmiyor. Building popup açıkken bir yan panel ya da
başlangıç info kartı olarak gösterilebilir.

### 16. Timeline Hız Kontrolü

`MS_PER_YEAR = 180` hardcode. Kullanıcı play hızını kontrol edemiyor.
Timeline üstüne `0.5× / 1× / 2×` toggle eklenebilir.

### 17. Globe → City Geçişi Siyah Flash

Globe'dan şehre geçerken `CityLoadingScreen` devreye giriyor ama bir kare
siyah flash oluyor. Globe'da `opacity: 0` → `CityExperience` `opacity: 0`
başlayıp animate → siyah flash ortadan kalkar.

### 18. Undated Bina Pulse Çok Agresif

`colorUndated` her RAF frame'de RGB değişiyor. Şehirde labeled building'ler
sabit renkte, labeled-olmayanlar titreşiyor. Bu dikkat dağıtıcı. Animasyon
daha yavaş (sin period 3-4s) ve daha düşük amplitude ile daha az dikkat çeker.

---

## Özet — En Yüksek ROI Sırası

| # | İş | Süre | Etki |
|---|---|---|---|
| 1 | Satellite opacity + material.ambient | 15 dk | ★★★★★ |
| 2 | --font-mono token düzelt | 5 dk | ★★★★☆ |
| 3 | Globe wordmark ekle | 20 dk | ★★★★☆ |
| 4 | Camera recenter butonu | 30 dk | ★★★☆☆ |
| 5 | Timeline era color strip | 45 dk | ★★★☆☆ |
| 6 | Keyboard shortcut hint | 10 dk | ★★★☆☆ |
| 7 | Sol alt HUD birleştir | 20 dk | ★★★☆☆ |
| 8 | Building popup null state | 15 dk | ★★☆☆☆ |
| 9 | Globe hint fade out | 10 dk | ★★☆☆☆ |
| 10 | Night mode body transition | 10 dk | ★★☆☆☆ |
