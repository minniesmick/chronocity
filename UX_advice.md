# ChronoCity UX Advice
*Koddan çıkarılmış gözlemler — değiştirmeden önce hocanın onayına sunulabilecek şeyler de var.*

---

## 1. Globe Ekranı — Premium Upgrade Listesi (Öncelik Sırasıyla)

### 1A. Yıldız Alanı (En Kolay, En Büyük Etki)

Globe şu an saf siyah zemin üzerinde. Siyah zemin ucuz durur.
`GlobeSelector.tsx`'teki canvas'ın arkasına (ya da CSS `::before`) 800–1200 noktalı, `opacity: 0.4` bir canvas yıldız alanı ekle.
Three.js `Points` ile trivial: `THREE.BufferGeometry`, `Float32Array` random pozisyonlar, `THREE.PointsMaterial`.
Gece modunda `opacity: 0.55`, gündüzde `opacity: 0.18`. Hiçbir şey yapmadan sanki uzaydasın hissi verir.

### 1B. Connector Line'larını Canlandır

Şu an SVG `strokeDasharray="5 4"` statik. Hiçbir enerji yok.
`stroke-dashoffset` property'sini CSS `animation` ile `-9px`'den `0`'a döngüsel hareket ettir:
```css
@keyframes dash-flow {
  to { stroke-dashoffset: -9; }
}
.globe-svg-layer line[data-visible="true"] {
  animation: dash-flow 0.4s linear infinite;
}
```
Sonuç: Globe'dan şehir kartına doğru enerji "akıyor" gibi görünür. Apple Maps'teki route pulse animasyonu efekti.

### 1C. Atmosfer Rim — Daha Dramatik

`atmMat.opacity = 0.10` çok ince. Premium glob görsellerde rim `0.18–0.25` arası.
Gece modunda mavi (`#2b6fb0`), gündüzde açık mavi-beyaz (`#87ceeb`) yap. Şu an yapılıyor ama gece opacity 0.10, gündüz 0.06 — her ikisi de çok az.
Gece için `0.20`, gündüz `0.10` dene.

### 1D. Mouse Parallax — Globe Nefes Alıyor

Şu an glob tamamen statik (sadece kendi ekseni etrafında dönüyor, kamera hiç hareket etmiyor).
Canvas üzerinde mouse pozisyonunu track et ve kamerayı `±0.15` birim hafifçe kaydır:
```js
camera.position.x = mouseX * 0.15;  // lerp ile değil, direkt — RAF'ta zaten çalışıyor
camera.position.y = 0.15 - mouseY * 0.10;
camera.lookAt(0, 0, 0);
```
RAF closure'ın içinde zaten mouse koordinatları var (`mouse.x`, `mouse.y`). Sadece camera positioning ekle.
Sonuç: Globe sanki gerçek hacimli, kullanıcıya "tepki veriyor" hissi.

### 1E. City Card Entrance — Spring ile Slide-In

Şu an kartlar `opacity` toggle ile anında görünüyor/kayboluyor (CSS `transition: opacity 0.2s`).
Her kart için Framer Motion yerine saf CSS: seçili kart `translate(tx, ty) scale(0.94)` → `scale(1)` + `opacity: 0 → 1`, 220ms, `cubic-bezier(0.16, 1, 0.3, 1)`.
Ama bu DOM manipülasyonu RAF içinde olduğu için dikkatli: class toggle yerine inline style `transform` zaten yapılıyor, `transition` property'si CSS'te zaten var. Sadece `scale` ekle: seçilince `scale(1)`, değilken `scale(0.94)`.

### 1F. "FLY TO" Butonu — Glow on Hover

Şu an düz border-left: 2px solid city-color ile bir düğme. Premium versiyon:
- Hover'da butonun `background`'ı `rgba(city-color, 0.12)` → `rgba(city-color, 0.20)` geçiş yapsın
- `box-shadow: inset 0 0 0 1px rgba(city-color, 0.30)` ekle hover'da
- Metin başına SVG rocket icon yerine `›` zaten var ama soluna `▲` (veya rotated) ekle
Bu zaten `--city-color` CSS custom property ile var, sadece CSS'te hover state eksik.

### 1G. Globe'a Zoom-In Navigasyon Efekti

`navigate('/city/${id}')` çağrılmadan önce:
1. Seçili şehrin 3D world pozisyonunu al
2. Kamerayı o yöne doğru 400ms lerp ile çek (`camera.position.lerp(targetPos, 0.1)` × n frame)
3. Sonra `navigate()` çağır

Şu an: tık → loading screen. İstenen: tık → glob o şehire doğru "uçuyor" → loading screen.
Bu ~40 satır RAF değişikliği.

### 1H. Wordmark'a Subtile Shimmer

`CHRONO CITY` kelimesi şu an statik. Çok ince bir `background: linear-gradient(90deg, ...)` animasyon ile "canlı" görünür. Tek satır CSS. Ama dikkat: `MOTION_INTENSITY` bağlamında bu çok ince olmalı, dikkat çekici değil.

---

## 2. Şehir Ekranı — Satellite + Bina Uyumsuzluğu

Bu projenin en büyük görsel sorusu. Üç katman çarpışıyor:
1. **Esri World Imagery** — foto-gerçekçi uydu görüntüsü
2. **Extruded building polygons** — düz renkli 3D prizmatik bloklar
3. **Era renklendirmesi** — kırmızı/turuncu/yeşil çatılar

Bu üçü aynı anda görünürse `realistic × abstract × data` üçlemesi olur ve hiçbiri iyi görünmez.

### Çözüm: "Sizi seçin" — ya gerçekçi ya da data viz

**Önerilen yol: Data Viz moduna basın**

Satellite layer opacity'i şu değerlerden:
- Gündüz: `0.80` → `0.45`'e indir
- Gece: `0.45` → `0.28`'e indir

Bu sayede uydu görüntüsü **referans** olarak kalır (yani hangi şehirde olduğun hissedilir) ama baskın görsel unsur bina geometrisi olur. Tokyo gece modunda bakıldığında Blade Runner estetiğine yaklaşır.

`MapCanvas.tsx:141`:
```ts
opacity: isDayMode ? 0.45 : 0.28,  // şu an: isDayMode ? 0.80 : 0.45
```

**Ek iyileştirme: Vignette overlay**

Haritanın kenarlarına koyu bir radial-gradient overlay ekle (CSS, `pointer-events: none`):
```css
.map-canvas::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 85% 80% at 50% 50%, transparent 55%, rgba(10,10,15,0.55) 100%);
  pointer-events: none;
  z-index: 1;
}
```
Bu kenarları karartarak gözü merkeze çeker ve "fotoğraf üstüne bina" uyumsuzluğunu maskeler.

**Gece modu: Wireframe outline ekle**

Gece modunda binalara `wireframe: true` VEYA mevcut solid binalar üstüne ince `getLineColor` ekle. DeckGL'de `GeoJsonLayer` hem `extruded: true` hem de `wireframe: false` olduğunda, binaların çatısında outline yok. Bina silüetleri görünür ve sokak-ışığı estetiği kazanılır. `MapCanvas.tsx`'te:
```ts
wireframe: !isDayMode,  // gece wireframe, gündüz solid
```

---

## 3. Top/Bottom Bar — Sticky mi Yapmalı?

**Kısa cevap: Şu an zaten sabit, sorun değil.**

`city-exp__top` ve `bottom-hud` sınıfları `position: fixed` ya da `position: absolute` ile map üzerinde. Kullanıcı haritayı kaydırınca kaybolmuyorlar. Bu doğru.

**Ama glass efekti yok — bu eksik.**

Şu an top bar `background: linear-gradient(to bottom, rgba(10, 10, 15, 0.80) 0%, transparent 100%)`. Bu işlevsel ama premium değil.
`backdrop-filter: blur(16px) saturate(160%)` ekle. Sprint1.css'te `.city-exp__top`'a:
```css
.city-exp__top {
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  background: rgba(10, 10, 15, 0.72);  /* solid fallback gerekmiyor, blur yeterli */
  border-bottom: var(--border-glass);
}
```
Bottom HUD için de aynı muamele. Şu an hiç border yok, ekle: `border-top: var(--border-glass)`.

---

## 4. Diğer Gözler Çarpanlar

### 4A. Yıl Göstergesi — Büyük Mono Text

Şehir ekranında zaman çizelgesi var ama şu anki yıl sadece küçük text olarak TimelineBar'da görünüyor.
Sol üst köşeye `position: absolute, z-index: 5` büyük mono text overlay ekle:
```
1987
```
`font-size: clamp(4rem, 8vw, 7rem)`, `opacity: 0.07`, `color: white`, `pointer-events: none`.
Bu arka plan dekorasyon olarak yıl değiştikçe fade-through yapar. Müze-grade zaman hissi verir.

### 4B. Loading Screen → City Transition

`CityLoadingScreen` kapanırken (`onReady`) altındaki harita reveal oluyor. Şu an loading ekranı `opacity: 0`'a çıkıyor, altı görünüyor.
Daha sinematik: Loading ekranı kapanırken aynı anda kamera yukarıdan aşağı `pitch: 0 → 50` ile iniyor gibi görünsün (zaten `useEffect` ile yapılıyor ama loading ekranı onu maskiliyor).
Yani şu an doğru çalışıyor — ama bunun farkında olmak önemli, bozma.

### 4C. EraLegend + TimelineBar Entegrasyonu

Bottom HUD'da şu an `EraLegend` + `TimelineBar` + `ReplayButton` yan yana. EraLegend ve TimelineBar'ın bağımsız olmak yerine tek bir glassmorphic panel içinde olması daha temiz görünür.

### 4D. Keyboard Shortcut Overlay — Daha İyi Position

Şu an overlay tüm ekranı kaplıyor (click-to-dismiss). Bunun yerine sadece sağ tarafta küçük bir kart olsa (ekranda başka şeyler görünebilsin) UX daha iyi olur. Ama bu ufak bir tercih meselesi.

### 4E. Building Popup — Overflow

`.bpop__name` içinde `white-space: nowrap; overflow: hidden; text-overflow: ellipsis` var. "Yapım yılı bilinmiyor" string'i yeterince geniş (`260px` popup için sorun yok). Ama çok uzun yapı adları kırpılıyor. Bunu iki satıra izin ver: `white-space: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical`.

### 4F. City Cards'ta Stats Eksikliği

11 şehirden bazılarında `stats` yok (`hasBuildingData: false` olanlar). Bu şehirlere tıklandığında kart content boş görünüyor. "Veri yakında geliyor" gibi bir placeholder ekle.

### 4G. Gündüz/Gece Toggle — Globe'da Texture Geçiş

Şu an gündüz/gece switch anında oluyor (texture `needsUpdate = true`). Aralarında 300-400ms cross-fade yapılabilir: iki ayrı mesh, biri fade-in yaparken diğeri fade-out.

### 4H. Mobile — Globe Zoom

Globe FOV şu an 36. Mobil ekranda (<768px) glob çok küçük görünüyor. Mobil'de FOV'u 28'e indirmeyi veya kamera z'yi 5.8'e çekmeyi düşün.

---

## 5. Uygulanmaması Gereken Şeyler

- `backdrop-filter: blur()` her yerde değil — sadece top/bottom bar ve popup. Haritanın üstündeki her şeye blur eklemek GPU'yu boğar.
- Yıldız alanı canvas'ı `will-change: transform` ile işaretleme — statik kalacak, gereksiz layer.
- City card'lara photo placeholder ekleme (şu an yok) — bu scope'u genişletir, hoca onayı gerektirir.
- Her şeyi aynı anda yapma. 1A (yıldız) + 1B (connector animasyon) + 2 (satellite opacity) üç değişiklik = görsel etki büyük ama kod riski düşük. Buradan başla.

---

*Son güncelleme: 2026-06-22*
