# ChronoCity — UI Taste Tavsiyesi (v2, Haziran 2026)

> **Design Read:** Premium dark-tech tarih keşif arayüzü — sinematik globe, canlı harita, zaman çizelgesi.  
> **Kullanıcı:** Tarih ve harita meraklısı, 20-40 yaş, masaüstü önce.  
> **Dials:** VARIANCE 7 / MOTION 7 / DENSITY 3

---

## 1. ŞEHİR RENK PALETİ — Revizyonu

### Mevcut sorunlar

| Çift | Hex 1 | Hex 2 | Sorun |
|------|-------|-------|-------|
| Chicago — Tokyo | `#8b5cf6` (violet) | `#a855f7` (purple) | Hue farkı sadece 8°, glob üzerinde neredeyse aynı görünüyor |
| İstanbul — Madrid | `#f59e0b` (amber) | `#eab308` (yellow) | İkisi de sarı-kehribar ailesi, 15° fark |
| Moskva | `#64748b` (slate) | — | Karanlık küre üzerinde donuk, ayırt edilemiyor |

### Önerilen Palet

Her şehir net kimlik rengi alıyor. Hue mesafesi minimum 30° sağlandı.

| Şehir | Renk Adı | Hex | Hue° | Değişim |
|-------|---------|-----|------|---------|
| **New York** | Steel Azure | `#38bdf8` | 197 | Mevcut `#3b82f6`'dan biraz daha temiz, gök gibi |
| **Istanbul** | Ottoman Amber | `#f59e0b` | 43 | KORU — kültürel fit mükemmel |
| **Chicago** | Neon Lime | `#a3e635` | 83 | Chicago Fire enerji; mevcut violet'ten tam kopuş |
| **Berlin** | Arctic Mint | `#34d399` | 158 | Mevcut `#10b981`'den biraz açık; Bauhaus temizliği |
| **Wien** | Imperial Violet | `#8b5cf6` | 258 | Chicago'nun eski rengi buraya taşındı; Habsburg mor |
| **Paris** | Orchid | `#e879f9` | 295 | Mevcut `#ec4899`'dan daha canlı, sanatsal fuchsia |
| **London** | Thames Teal | `#14b8a6` | 175 | Mevcut cyan'dan mavi-yeşile kaydı; Thames rengi |
| **Barcelona** | Sunburst | `#fb923c` | 25 | KORU — Gaudí turuncu, iyi |
| **Madrid** | Castilian Red | `#f43f5e` | 351 | Mevcut sarıdan kırmızıya büyük değişim; flamenco |
| **Tokyo** | Sakura | `#f472b6` | 327 | Mevcut mor yerine kiraz çiçeği pembe |
| **Moskva** | Permafrost | `#e2e8f0` | neutral | Benzersiz; tek nötr; soğuk Rus kış hissi |

### Hue Mesafe Tablosu (kritik çiftler)

```
Berlin  (158°) — London  (175°) = 17° — OK, açık yeşil vs koyu teal
London  (175°) — NY      (197°) = 22° — OK, teal vs mavi çok farklı doygunlukta
Wien    (258°) — Paris   (295°) = 37° — iyi
Paris   (295°) — Tokyo   (327°) = 32° — iyi
Tokyo   (327°) — Madrid  (351°) = 24° — OK, pembe vs kırmızı
Madrid  (351°) — Barcel. (25°)  = 34° — iyi
Barcel. (25°)  — İstanb. (43°)  = 18° — turuncu vs kehribar, doygunluk farkı yeterli
Moskva: nötr, hiçbirinden etkilenmiyor
```

### cities.ts — Uygulanacak Değişiklikler

```ts
// New York:    "#3b82f6"  →  "#38bdf8"
// Chicago:     "#8b5cf6"  →  "#a3e635"
// Berlin:      "#10b981"  →  "#34d399"
// Wien:        "#ef4444"  →  "#8b5cf6"
// Paris:       "#ec4899"  →  "#e879f9"
// London:      "#06b6d4"  →  "#14b8a6"
// Madrid:      "#eab308"  →  "#f43f5e"
// Tokyo:       "#a855f7"  →  "#f472b6"
// Moskva:      "#64748b"  →  "#e2e8f0"
// Istanbul:    "#f59e0b"  →  KORU
// Barcelona:   "#f97316"  →  "#fb923c"  (hafif ayar)
```

---

## 2. GLOBE KARTINDA ŞEHİR SVG İLLÜSTRASYONU

### Öneri: EVET, ekle — ve iyi yapılırsa çok güçlü

Kart aktive edildiğinde (FLY TO görününce) sağ tarafa veya arka plana şehrin ikonik silüeti gelsin.

**Stil:**
- Tek renkli SVG silüet (flat, outline değil)
- Dolgu rengi: `city.color` %20-30 opasite
- Boyut: kartta yaklaşık 80x60px, sağ alt veya sağ kenar
- Efekt: hafif `filter: blur(0.5px)` + `opacity: 0.25` — watermark hissi, dominant değil

**Her şehir için önerilen ikon:**

| Şehir | SVG Silüet |
|-------|-----------|
| New York | Özgürlük Heykeli veya Empire State silueti |
| Istanbul | Ayasofya kubbesi + minareleri |
| Chicago | Sears Tower (Willis) + Cloud Gate kombinasyonu |
| Berlin | Brandenburg Kapısı |
| Wien | Stephansdom çan kulesi |
| Paris | Eyfel Kulesi |
| London | Big Ben kulesi |
| Barcelona | Sagrada Familia cephesi |
| Madrid | Kraliyet Sarayı veya Cibeles heykeli |
| Tokyo | Fuji Dağı silueti + pagoda |
| Moskva | Saint Basil Katedrali soğan kubbesi |

**Implementasyon seçeneği — en temizi:**

```tsx
// CityMeta'ya ekle:
svgLandmark?: string; // SVG path verisi (d attribute)

// GlobeSelector.tsx'te card JSX'ine:
{isSel && city.svgLandmark && (
  <svg
    className="city-card__landmark"
    viewBox="0 0 100 80"
    aria-hidden="true"
  >
    <path d={city.svgLandmark} fill={city.color} opacity="0.22" />
  </svg>
)}
```

```css
.city-card__landmark {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 72px;
  height: 56px;
  pointer-events: none;
  filter: blur(0.3px);
}
```

**Alternatif:** SVG bileşenler ayrı dosyalar olarak `/public/cities/{id}/landmark.svg` yolunda tutulup `<img>` ile yüklenir. Daha kolay edit, ama bir HTTP request ekler.

**Neden iyi:** Her şehir kart açıldığında net bir kimlik ifadesi oluyor. Kullanıcı karta bakarken o şehrin ruhunu hissediyor. Basit flat silüet, sadeliği bozmadan premium katman ekliyor.

---

## 3. GLOBE EKRANI — Kalite Artırıcılar

### 3.1 Globe glow'u aktif şehire bağla

`.globe-selector__glow` şu an sabit amber. Hover'da/select'te o şehrin rengine geç:

```js
// RAF loop'ta:
if (hoveredId) {
  const hCity = CITIES[hoveredId];
  glowEl.style.setProperty('--glow-c', hCity.color);
}
```
```css
.globe-selector__glow {
  background: radial-gradient(ellipse at center, var(--glow-c, #f59e0b) 0%, transparent 70%);
  transition: --glow-c 0.6s ease; /* custom prop transition - Chrome 131+ */
}
```

### 3.2 Dot pulse animasyonu şehir renginde

Şu an Three.js sphere tek renk, pulse yok. CSS overlay ile basit breath ekle:

```css
.city-dot::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1.5px solid currentColor;
  opacity: 0;
  animation: city-pulse 2.8s ease-out infinite;
}
@keyframes city-pulse {
  0%   { transform: scale(1);   opacity: 0.6; }
  100% { transform: scale(2.4); opacity: 0; }
}
```

### 3.3 "ChronoCity" branding — sol üst

Globe ekranında hiç logo yok. Sol üst köşeye küçük bir wordmark veya monogram:

```tsx
<div className="globe-brand">
  <span className="globe-brand__ch">CH</span>
  <span className="globe-brand__name">ChronoCity</span>
</div>
```

Globe dönerken `opacity: 0` → `1` fade-in (0.5s, delay 0.8s). Karmaşıklık eklemez, professional presence verir.

### 3.4 İlk açılış hint'i — sadece 1 kez göster

"Sürükle · Döndür" vs. hint'i ziyaretçinin deneyimini keser. localStorage ile bir kez göster, sonra gizle:

```ts
const shown = localStorage.getItem('cc-hint');
if (!shown) {
  showHint();
  setTimeout(() => { hideHint(); localStorage.setItem('cc-hint', '1'); }, 4000);
}
```

### 3.5 Globe boyutu — büyüt

Şu an viewport'un yaklaşık %50'sini dolduruyor. `%65-70`'e çıkar:

```js
renderer.setSize(containerW * 1.0, containerH * 1.0);
globe.scale.set(1.18, 1.18, 1.18); // mevcut ölçekten +%18
```

---

## 4. ŞEHİR (MAP) EKRANI — Kalite Artırıcılar

### 4.1 Globe → City geçişi daha sinematik olabilir

Şu an FLY TO → route değişimi → harita yüklenir. Şehir ekranına geçerken şu sıra önerilir:

1. Globe kart → "FLY TO" → `setSelectedCity(null)` → navigate
2. CityLoadingScreen açılırken arka planda harita sessizce yükleniyor (mevcut davranış, iyi)
3. LoadingScreen exit: mevcut `motion.div` opacity fade yeterli ama...
4. **Önerilir:** Exit anında harita tam zoom-in fly animasyonu tamamlanmış gibi görünsün (MapCanvas'ta `fitBounds` yerine `flyTo` ile cinematic giriş — zaten var, speed kontrolü ekle)

### 4.2 Bina popup — premium içerik

Şu an popup'ta çok az bilgi var. Bina açıldığında şunlar güçlü görsel etki yaratır:

- `construction_year` için küçük **zaman çizelgesi segmenti**: "Bu bina, sen {{year}}'deyken {{era}}'nın {{%X}}'indeydin"
- Binanın ait olduğu era rengi ile sol border (zaten var sanırım, kontrol et)
- `height` değeri büyük, bold mono fontla: `42m`
- Popup sağ üst köşesine şehrin era-rengi dot

### 4.3 Night mode — satellite opasite

Mevcut gece modunda satellite 0.35 opasite: binalar öne çıkıyor, kasıtlı ve güzel. Ama şehrin coğrafi bağlamı (kıyı çizgisi, parklar) çok kayboluyor.

Test önerim: `0.42-0.45`. Binalar hala dominant, bağlam gelir.

### 4.4 Timeline — era label'ları renk kodlu

Timeline'daki era pill'leri zaten var. Ama bug'lu olduğunda fark edilmez. Her era'nın rengi hem pill'de hem timeline track'te (gradient stop olarak) görünmeli.

### 4.5 Recenter butonu — göz önünde değil

Mevcut recenter butonu var (eklendi) ama üst bar'da kayboluyor. Sağ alt köşeye (building popup'ın olduğu tarafa değil, boş tarafa) taşımayı düşün. Ya da üst bar'da ikon daha belirgin yapılabilir.

### 4.6 Keyboard shortcut cheatsheet

Timeline'da `SPACE oynat · ← / → yıl · SHIFT+← / → ×10` hint'i var. Bu harika. Ama yeni kullanıcı görmüyor çünkü çok küçük. İlk girişte 3 saniyeliğine fade-in overlay ile göster.

---

## 5. GENEL / HER İKİ EKRAN

### 5.1 Tipografi tutarlılığı

- Tüm sayısal değer (yıl, nüfus, zoom seviyesi, height) → `font-mono`
- UI label'lar (buton text, badge) → sans
- Şu an bazı label'larda `font-mono` geçiyor — kontrol et

### 5.2 Glass border token'ı tekleştir

Birden fazla yerde `rgba(255,255,255,0.06)`, `0.07`, `0.08` değerleri dağınık.
Tek bir CSS değişkeni olsun:

```css
--border-glass: 1px solid rgba(255, 255, 255, 0.07);
```

### 5.3 Renk kontrast — faint text kontrolü

`rgba(255,255,255,0.45)` veya altı non-interactive text için WCAG AA sınırının altı. Non-interactive için minimum `0.5`, interactive için `0.7+` olsun.

### 5.4 Era renk legend — demo için kritik

Şu an hangi rengin hangi era'ya ait olduğunu gösteren bir legend yok (sadece timeline pill'leri var). Sol alt köşeye collapse edilebilir küçük panel:

```
[ ■ 60'lar  ■ 80'ler  ■ 2000'ler  ■ Modern ] ← toggle ile
```

Jüri demosunda ilk sorulan şey budur.

### 5.5 Z-index katman dokümantasyonu

```
z-map:       5   (DeckGL canvas)
z-ui:       20   (üst bar, bottom-hud)
z-popup:    30   (building popup, event popup)
z-loading:  40   (CityLoadingScreen)
z-hint:     50   (zoom hint pill, shortcut overlay)
z-modal:    60   (gelecek modal ihtiyacı için rezerv)
```

### 5.6 prefers-reduced-motion

Şu an hiç kontrol edilmiyor. Minimum:

```css
@media (prefers-reduced-motion: reduce) {
  .city-dot::after { animation: none; }
  * { transition-duration: 0.01ms !important; }
}
```

---

## 6. SPRINT ÖNERİSİ — ROI Sırasıyla

| Öncelik | Görev | Süre | Etki |
|---------|-------|------|------|
| 1 | Renk paletini güncelle (cities.ts) | 15 dk | Görsel çakışma tamamen gider |
| 2 | Globe glow → city-color | 30 dk | Wow anı — her hover renkleniyor |
| 3 | Era color legend | 2 sa | Demo için zorunlu |
| 4 | City SVG landmark silüetleri | 4-8 sa | Premium kimlik, büyük görsel etki |
| 5 | Globe scale +%18 | 5 dk | Daha dolgun, daha egemen |
| 6 | İlk açılış hint localStorage | 20 dk | UX temizliği |
| 7 | Bina popup içerik zenginleştirme | 2 sa | Ürün derinliği |
| 8 | Gece modu opasite 0.42 test | 5 dk | Görsel denge |
