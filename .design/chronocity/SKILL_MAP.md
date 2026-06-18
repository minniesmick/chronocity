# ChronoCity — Skill Haritası

Bu dosya Claude Code'a hangi işlemde hangi skill dosyasını kullanacağını söyler.
Her yeni konuşmada önce bu dosyayı oku, sonra ilgili skill'i oku, sonra kodu yaz.

---

## Skill Dosyaları (Mutlak Path)

```
.design/skills/frontend-design.md
.design/skills/ui-ux-pro-max.md
.design/skills/design-tokens.md
.design/skills/information-architecture.md
.design/skills/design-review.md
```

---

## Ne Zaman Hangi Skill

### 🎨 Yeni component yazarken
1. `.design/skills/frontend-design.md` oku
2. `.design/skills/ui-ux-pro-max.md` → `--design-system` komutunu çalıştır
3. `.design/chronocity/DESIGN_BRIEF.md` estetik yönü kontrol et
4. `.design/chronocity/TASKS.md`dan task'ı bul, tamamlandı işaretle

**Tetikleyici:** "X component yaz", "Y ekranını build et", "Z sayfasını kur"

---

### 🎨 Design token / CSS değişkeni ayarlarken
1. `.design/skills/design-tokens.md` oku
2. `.design/chronocity/DESIGN_BRIEF.md` → Aesthetic Direction bölümü
3. `src/styles/tokens.css` oluştur veya güncelle

**Tetikleyici:** "token ekle", "renk değiştir", "spacing güncelle", "dark mode"

---

### 🗂️ Yeni sayfa veya route eklerken
1. `.design/skills/information-architecture.md` oku
2. `.design/chronocity/INFORMATION_ARCHITECTURE.md` varsa kontrol et
3. Mevcut React Router yapısını tara (`src/router/` veya `App.tsx`)

**Tetikleyici:** "yeni sayfa", "route ekle", "navigation", "URL yapısı"

---

### ✅ Bir sprint/milestone bitince review
1. `.design/skills/design-review.md` oku
2. `localhost:5173` üzerinde çalışan uygulamanın screenshot'larını al
3. `.design/chronocity/DESIGN_BRIEF.md`e karşı karşılaştır
4. `.design/chronocity/DESIGN_REVIEW.md` dosyasına yaz

**Tetikleyici:** "review yap", "brief'e uyuyor mu", "kontrol et", "QA"

---

### 🎯 Her zaman geçerli kurallar

- Her component yazmadan önce `src/` dizinini tara — duplicate yaratma
- Token kullan, hardcode hex/px yazma
- `TASKS.md`daki task'ı tamamlayınca `- [ ]` → `- [x]` yap
- Brief'te "Anti-references" yazan şeylerden uzak dur (Bootstrap, generic kart grid, beyaz bg)
- Aesthetic: **Tekno-sinematik minimalizm** — koyu zemin `#0A0A0F`, amber aksan `#F59E0B`
- 60fps hedef — shader/animation yazarken `transform/opacity` kullan, `width/height` değil

---

## Proje Referans Dosyaları

| Dosya | İçerik |
|-------|--------|
| `.design/chronocity/DESIGN_BRIEF.md` | Tüm tasarım kararları, component listesi, user flow |
| `.design/chronocity/TASKS.md` | Sprint bazlı task listesi, ilerleme takibi |
| `.design/chronocity/INFORMATION_ARCHITECTURE.md` | Sayfa yapısı, routing, nav modeli (oluşturulacak) |
| `.design/chronocity/DESIGN_REVIEW.md` | Review bulguları (sprint sonunda oluşturulacak) |
| `src/styles/tokens.css` | Design tokens — tüm CSS değişkenleri |
| `public/cities/` | Şehir verisi: events, music, videos |

---

## Stack Hızlı Referans

```
Framework   React 18 + Vite + TypeScript
3D          Three.js (Globe), deck.gl (harita extrusion)
Shader      GLSL (WebGL2) — uTime, uDayNight uniform'ları
Audio       Web Audio API + Tone.js — crossfade, FFT
Animation   Framer Motion (UI) + GSAP (kamera, kamera path)
State       Zustand — global t parametresi, aktif şehir, era
Routing     React Router v6
Realtime    WebSocket → FastAPI backend (backend/main.py)
Maps        Google Maps JS API + react-map-gl
AI          Gemini API — streaming, GeminiReportDrawer
PWA         vite-plugin-pwa
```

---

## Kritik Global State (Zustand)

```typescript
// Tüm sistem bu store'dan beslenir
{
  t: number,              // 0.0–1.0 — zaman parametresi, tüm sisteme yayılır
  activeCity: CityId,     // 'istanbul' | 'new-york' | 'chicago' | 'berlin' | 'vienna'
  era: EraId,             // '1960s' | '1980s' | '2000s' | 'modern'
  isDayMode: boolean,     // gece/gündüz shader uniform
  isPlaying: boolean,     // timeline otomatik çalıyor mu
  activeEvent: Event | null,
  audioReady: boolean,    // Web Audio API user gesture sonrası
}
```

---

## Şehir Renk Paleti (Globe noktaları)

```
İstanbul  → #F59E0B (amber)
New York  → #3B82F6 (mavi)
Chicago   → #8B5CF6 (mor)
Berlin    → #10B981 (yeşil)
Viyana    → #EF4444 (kırmızı)
```

---

## Data Klasörü Yapısı

```
public/
  cities/
    istanbul/
      loading-video.mp4
      music/
        1960s.mp3
        1980s.mp3
        2000s.mp3
        modern.mp3
      events/
        1999-08-17/
          info.json    ← {date, title, shortDesc, type, category, coordinates, wikiSlug}
          cover.jpg
    new-york/  ...
    chicago/   ...
    berlin/    ...
    vienna/    ...
```

`type` değerleri: `"positive"` | `"negative"` | `"neutral"`
