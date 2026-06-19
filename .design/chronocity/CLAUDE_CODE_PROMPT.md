# ChronoCity — Claude Code Master Prompt

Aşağıdaki metni Claude Code'a ilk mesaj olarak gönder.
Proje klasörünü Claude Code'a açtıktan sonra yapıştır.

---

## PROMPT (kopyala-yapıştır)

Sen ChronoCity projesinin baş geliştiricisisin. Bu proje; İstanbul, New York, Chicago, Berlin ve Viyana'nın kentsel dönüşümünü zaman içinde 3D olarak gösteren, her dönemin ses kimliğini procedural olarak çalan ve canlı verilerle şehrin nabzını hissettiren bir web uygulamasıdır.

**Önce şu dosyaları oku, sonra kod yaz:**

1. `.design/chronocity/SKILL_MAP.md` — hangi işlemde hangi skill'i kullanacağını söyler
2. `.design/chronocity/DESIGN_BRIEF.md` — tüm tasarım kararları, component listesi, user flow
3. `.design/chronocity/TASKS.md` — sprint bazlı task listesi

**Çalışma kuralların:**

- Her yeni component yazmadan önce `src/` dizinini tara, duplicate yaratma
- Her task tamamlanınca `TASKS.md`da `- [ ]` → `- [x]` işaretle
- Token kullan, hardcode hex/px yazma — `src/styles/tokens.css` referans al
- Estetik: tekno-sinematik minimalizm. Koyu zemin, amber aksan. Generic AI çıktısı üretme.
- Performans birinci öncelik: shader'da `transform/opacity`, `width/height` değil. 60fps hedef.
- Brief'teki "Anti-references" listesine bak — bunlardan uzak dur

**Stack:**
React 18 + Vite + TypeScript, Three.js (Globe), deck.gl (harita), GLSL (WebGL2), Web Audio API + Tone.js, Framer Motion + GSAP, Zustand, React Router v6, FastAPI (WebSocket backend), Google Maps JS API, Gemini API (opsiyonel)

**Global state (Zustand) — tüm sistem buradan beslenir:**
```typescript
{
  t: number,           // 0.0–1.0, zaman parametresi, shader + audio + particle hepsi buna bağlı
  activeCity: CityId,
  era: EraId,
  isDayMode: boolean,
  isPlaying: boolean,
  activeEvent: Event | null,
  audioReady: boolean,
}
```

**Mevcut durum: S0 + S1 + S2 + S3 (kısmi) TAMAMLANDI ✅**

- Design tokens, scaffold, Zustand store, FastAPI backend → hazır
- deck.gl 3D skyline, construction_year time morph, DayNightToggle → çalışıyor
- **Era renk sistemi**: `colorByEra(year)` 7 dönem bandı + `colorUndated(frame)` pulse → hazır
- **PRODUCT.md + DESIGN.md** → proje kökünde hazır (impeccable skill için)
- **11 şehir verisi** (`hasBuildingData: true` hepsi, `public/cities/{id}/buildings.geojson`):
  - NYC 6.5K bina 3.4MB | Berlin 27.5K 12MB | Vienna 18K 8.3MB | Chicago 4.5K 1.6MB
  - İstanbul 5K 1.4MB | Paris 13.7K 6MB | London 26.9K 9.5MB | Tokyo 26K 7.4MB
  - Madrid 14.2K 6.2MB | Barcelona 19.5K 8.4MB | Moscow 8.2K 3.2MB
- **Sprint 2 tamamlandı**: GlobeSelector (Three.js, scale-in animasyon, amber glow) + IntroScene (scanlines, stagger) + CityLoadingScreen (typewriter, progress) + React Router v6 + AnimatePresence
- **Sprint 3 kısmen tamamlandı**:
  - TimelineBar: glassmorphism panel, yıl göstergesi (blur geçişi), era pill radio'lar, play/auto-play, keyboard ←/→/Space
  - YearIndicator + EraRadio: `eraFromYear()` lib/time.ts'te, `/public/cities/{id}/music/{eraId}.mp3` placeholder'lar hazır (44 adet)
  - EventMarker: timeline üstünde renkli noktalar (positive/negative/neutral), proximity fade, pulse, hover → `setActiveEvent`
  - `useCityEvents` hook: `activeCity` store → `/public/cities/{id}/events/info.json` fetch
  - **Berlin + İstanbul event verisi** hazır (9'ar olay, `public/cities/{id}/events/info.json`)
- **Animated Icons**: `src/components/icons/` — 31 adet Framer Motion animated SVG icon (arrow-narrow-left/right, moon, brightness-down, player, clock, refresh, globe, volume-2/x, layers, sliders-horizontal, map-pin, info-circle, sparkles, brain-circuit, chart-line, locate, satellite-dish, keyframes, target, filter, heart, star, download, expand, x + daha fazlası). API: `size`, `color`, `strokeWidth`, `className` props + `AnimatedIconHandle` ref.
- **Polish + Animate tamamlandı**: globe mount scale-in, header slide-down, timeline slide-up, yıl blur geçişi, intro scanlines, label hover glow

**Sıradaki görev: S3 kalan task'ları**

TASKS.md'da S3'te bekleyen:
1. **EventPopup** — EventMarker hover/click → slide-up glassmorphism kart (başlık + shortDesc + tip rengi + "Daha fazla" CTA). `activeEvent` store'dan okur.
2. **ReplayButton** — `refresh-icon` kullan, float bottom-right, tıklanınca t=0 set + setPlaying(true)

Sonra S4 → EraAudioEngine (Web Audio API + Tone.js, `/public/cities/{id}/music/{eraId}.mp3`)

Başlamadan önce `src/` dizinini tara, mevcut component'lere bak.

---

## CLAUDE CODE'A ATACAĞIN DOSYALAR

Proje klasörüne şunları koy, Claude Code bu klasörü açsın:

```
chronocity/                    ← boş proje klasörü
  .design/
    chronocity/
      DESIGN_BRIEF.md          ← ✅ hazır
      TASKS.md                 ← ✅ hazır
      SKILL_MAP.md             ← ✅ hazır
    skills/
      frontend-design.md       ← ✅ kopyala (aşağıda path)
      ui-ux-pro-max.md         ← ✅ kopyala
      design-tokens.md         ← ✅ kopyala
      information-architecture.md ← ✅ kopyala
      design-review.md         ← ✅ kopyala
```

**Skill dosyalarını nereden kopyalarsın:**
Windows path'leri (sen zaten biliyorsun, agent klasöründe bunlar var):
```
C:\Users\alper\.agents\skills\frontend-design\SKILL.md      → .design/skills/frontend-design.md
C:\Users\alper\.agents\skills\ui-ux-pro-max\SKILL.md        → .design/skills/ui-ux-pro-max.md
C:\Users\alper\.agents\skills\design-tokens\SKILL.md        → .design/skills/design-tokens.md
C:\Users\alper\.agents\skills\information-architecture\SKILL.md → .design/skills/information-architecture.md
C:\Users\alper\.agents\skills\design-review\SKILL.md        → .design/skills/design-review.md
```

PowerShell ile kopyala:
```powershell
$proj = "C:\Users\alper\PROJELER\chronocity\.design\skills"
New-Item -ItemType Directory -Force -Path $proj
$skills = "C:\Users\alper\.agents\skills"
Copy-Item "$skills\frontend-design\SKILL.md" "$proj\frontend-design.md"
Copy-Item "$skills\ui-ux-pro-max\SKILL.md" "$proj\ui-ux-pro-max.md"
Copy-Item "$skills\design-tokens\SKILL.md" "$proj\design-tokens.md"
Copy-Item "$skills\information-architecture\SKILL.md" "$proj\information-architecture.md"
Copy-Item "$skills\design-review\SKILL.md" "$proj\design-review.md"
```

---

## SPRINT BAŞI PROMPT ŞABLONU

Her yeni sprint'te Claude Code'a şunu söyle:

```
TASKS.md'da SPRINT [N]'i tamamla.
Başlamadan önce:
1. SKILL_MAP.md oku
2. Mevcut src/ yapısını tara
3. Her task için ilgili skill dosyasını oku
4. Tamamlananları TASKS.md'da işaretle
```

---

## COMPONENT BAŞI PROMPT ŞABLONU

Tek component için:

```
[Component adı] yaz.
- SKILL_MAP.md → frontend-design.md oku
- DESIGN_BRIEF.md → Component Inventory bölümüne bak
- src/ tara, duplicate var mı kontrol et
- tokens.css kullan, hardcode yazma
- Estetik: tekno-sinematik minimalizm, amber/koyu
- Bitince TASKS.md'da işaretle
```

---

## REVIEW PROMPT ŞABLONU

Sprint sonunda:

```
SPRINT [N] design review yap.
- SKILL_MAP.md → design-review.md oku
- localhost:5173 üzerinde screenshot al (1280px, 768px, 375px)
- DESIGN_BRIEF.md Aesthetic Direction ile karşılaştır
- .design/chronocity/DESIGN_REVIEW.md dosyasına kaydet
- Must Fix / Should Fix / Could Improve olarak listele
```
