# ChronoCity — UI Taste Tavsiyesi

> Design read: **3D bilim + sanat hibrid arayüz** — dark tech / premium consumer ortası.  
> Kullanıcı: harita ve tarih meraklısı, 18-35 yaş, masaüstü önce.  
> Dials: VARIANCE 7 / MOTION 7 / DENSITY 3

---

## GLOBE EKRANI

### Yapılanlar (iyi)
- Glassmorphism şehir kartları: doğru. `border-left: 2px solid city-color` güçlü ama sade kimlik.
- Küre scale-in animasyonu (80 frame eased) cinematic açılış hissi veriyor.
- Day/night toggle sağ üst: doğru pozisyon, konum mantıklı.
- Rotasyon durdur butonu sol alt: DayNightToggle ile köşegen denge yaratıyor. Devam et.

### Geliştirme Önerileri

**1. Şehir kartlarına mikro-elevation**  
Şu an hover'da sadece `scale(1.05)`. Kart hover'da `box-shadow: 0 8px 32px rgba(city-color, 0.3)` ekle. Renk nüanslı gölge = premium hissi.

**2. Başlık / intro text yok**  
Globe ekranında "ChronoCity" logosu veya küçük bir başlık yok. Sol üst köşeye ya `CH` monogram ya da küçük wordmark. Globe dönerken yavaş fade-in. Şu an küre tek başına yüzüyor.

**3. Şehir dot'larına pulse ring animasyonu (CSS, JS değil)**  
Three.js mesh'e ek olarak, dünya üzerindeki her şehir dot'una küçük bir CSS animated ring overlay (canvas üstüne absolute div ile) ekleme deneyin. Şu an Three.js halo sabit. Alternatif: Three.js `opacity` 0.3→0.6→0.3 loop (shader veya material.opacity lerp).

**4. Globe glow rengi sabit amber**  
`.globe-selector__glow` her zaman amber. Aktif şehir hover'ında glow rengini `city-color`'a kaydır. CSS custom property ile: `--glow-color: var(--city-color, #f59e0b)`. Hover state'te geçiş `transition: --glow-color 0.4s` (hala sınırlı browser desteği) ya da JS ile inline style güncelle.

**5. "Sürükle · Döndür · Bir şehre tıkla" hint'i**  
Şu an sonsuz pulse animasyonu. 3 saniye sonra `opacity: 0` yapıp gizle (localStorage ile "ilk ziyaret" kontrolü). Sürekli yanıp sönen hint deneyimli kullanıcıda gürültü.

**6. Zoom out yasak — ama globe küçük kalıyor**  
Küre biraz küçük. `globe.scale` 0.82→1.0 arttır. Viewport'un %60-65'ini doldurmalı, şu an %50 civarı.

---

## ŞEHİR (MAP) EKRANI

### Yapılanlar (iyi)
- Satellite basemap + era-colored binalar = güçlü kontrast. Gündüz tam opasite, gece 0.35 — doğru.
- minZoom=12 kısıtı + bbox extent optimizasyonu: hem UX hem perf doğru.
- Zoom sınır bildirimi (yeni eklendi): sade glassmorphism pill, süresi 1.6s — doğru dozaj.
- FlyTo animasyonu 2.2s, speed 1.4 — sinematik ama aşırı uzun değil.

### Geliştirme Önerileri

**1. Zoom sınır pill'i — ikon seçimi**  
`⊖` / `⊕` Unicode sembol yerine `@phosphor-icons/react`'ten `MinusCircle` / `PlusCircle` (thin weight) kullan veya mevcut `expand-icon.tsx`'i yeniden kullan. Unicode sembolleri farklı sistemlerde farklı render eder.

**2. Sol alt "zoom level" göstergesi (kalıcı)**  
Sadece sınırda değil, her zaman görünen küçük bir zoom seviyesi sayacı ekle: `14.5 ×` formatında, sol alt köşe, `font-mono 10px`. Haritacılık convention'ı. Timeline'la çakışmıyorsa yerleştir.

**3. Top bar — "geri" butonu daha belirgin olabilir**  
Şu an `ArrowNarrowLeftIcon + "geri"` text-only. Hafif glassmorphism pill ekle (DayNightToggle gibi). Şehir adı rengi (`city.color`) zaten var — "geri" butonu buna uyumlu olursa daha koherant.

**4. Building popup konumu**  
Mobil/küçük viewport'ta popup ekranın altına taşabilir. `x, y` koordinatından hesaplanan pozisyonun viewport kenarlarını check etmesi lazım: `Math.min(x, window.innerWidth - popupWidth - 16)`.

**5. Night mode — satellite 0.35 opasite çok düşük**  
Gece modunda arka plan neredeyse görünmez, binalar ön plana çıkıyor — bu kasıtlı ve güzel. Ama şehrin coğrafi bağlamı (ızgara yapısı, kıyı çizgisi) kayboluyor. Test et: `0.45-0.50` arası daha iyi denge sağlayabilir.

**6. Era renk legend**  
7 era var ama hiç bir yerde legend yok. Sol alt köşeye collapse edilebilir küçük bir panel: her era'nın renk kutusu + isim. `<details>` HTML elementi veya hover-expand motion.div. Sınav/demo için kritik.

**7. Frekans vizualizeri pozisyonu**  
Timeline alt bar'ın içinde mi yoksa üstünde mi yerleşiyor? Sağ alt köşeye taşı, 32px yükseklik kap. Şu an timeline ile görsel çatışma riski var.

**8. Animasyonsuz bina yüklemesi için skeleton**  
`loading=true` durumunda `.map-canvas__status "binalar yükleniyor…"` tek satır metin. Bunun yerine: merkeze küçük bir pulse ring (CSS, `border: 1px solid rgba(255,255,255,0.2)`) + aynı metin. Daha premium.

---

## GENEL / HER İKİ EKRAN

### Tip & Spacing

- **Font mono kullanımı tutarlı**: tüm label, badge, sayı = `var(--font-mono)`. Şu an bazı yerler sans geçiyor olabilir — denet.
- **Letter-spacing**: mono için `0.06-0.1em` tutarlı. `var(--tracking-wider)` yerine direkt değer kullan, CSS variable cascade'i debug edilmesi zor.
- **Spacing token dağılımı**: `--space-3, --space-5` çok atlıyor. `--space-4` nerede? Token aralıkları lineer mi exponential mi karar ver, karışık kalmasın.

### Renk & Kontrast

- **Ana aksent amber (#f59e0b)**: globe ekranında mantıklı. City ekranında kullanılmıyor — era renkleri öne çıkıyor. Bu iyi bir ayrım.
- **`--color-text-faint`** çok soluk — WCAG AA altında olabilir. En az `rgba(255,255,255,0.45)` interactive olmayan elementlerde; `0.65+` interactive text için.
- **Glass border**: `rgba(255,255,255,0.07)` birçok yerde. Bazı card'lar `0.08`, bazıları `0.07`. Tek bir token olsun: `--border-glass`.

### Motion

- **Framer-motion `ease: [0.16, 1, 0.3, 1]`** her yerde kullanılıyor — bu marka motion signature'ı oldu, iyi. Devam et.
- **RAF ile ~20fps frame counter** (MapCanvas): performans için doğru ama `setFrame(f => f + 1)` her 50ms React re-render tetikliyor. Pulse animasyonu için CSS `@keyframes` veya Three.js shader daha iyi olurdu.
- `prefers-reduced-motion` hiç check edilmiyor. Bitirme projesi jürisi için önce değil, ama not al.

### Şehir Ekranı Z-index Katmanları (belgelensin)

```
z-map:      5    (DeckGL canvas)
z-ui:       20   (üst bar, timeline)
z-popup:    30   (building popup, event popup)
z-loading:  40   (CityLoadingScreen)
z-hint:     50   (zoom hint pill)  ← yeni eklendi
```

---

## SPRINT ÖNERİSİ — En Yüksek ROI Sırasıyla

1. **Era color legend** — demo için zorunlu. 2 saat iş, görsel çok.
2. **Top bar "geri" glassmorphism pill** — cohesion. 30 dk.
3. **Zoom level kalıcı göstergesi** — haritacılık pro hissi. 20 dk.
4. **Globe glow rengi → city-color** — wow moment. 45 dk.
5. **Satellite gece opacity 0.45'e çek** — test et, beğenirsen merge. 5 dk.
6. **Globe scale 0.82 → 1.0** — küre büyüsün, dolsun. 5 dk.
