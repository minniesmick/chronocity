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

**Mevcut durum: SPRINT 0 + SPRINT 1 TAMAMLANDI ✅**

- Design tokens, scaffold, Zustand store, FastAPI backend → hazır
- deck.gl 3D NYC skyline, construction_year time morph, DayNightToggle → çalışıyor, doğrulandı
- NYC 6.550 bina verisi `public/cities/new-york/buildings.geojson` → hazır

**Sıradaki görevin: SPRINT 2'yi tamamla**

TASKS.md'daki SPRINT 2 task'larını sırayla yap:
1. GlobeSelector — Three.js 3D dünya, 5 şehir noktası
2. Bayrak & Şehir Label — hover type-on animasyonu
3. IntroScene — video loop + logo fade + enter CTA
4. CityLoadingScreen — şehir videosu + typewriter stats + progress bar
5. React Router v6 route'ları bağla (/ → Globe, /city/:id → CityExperience)

Her task için önce SKILL_MAP.md'a bak, ilgili skill dosyasını oku, sonra yaz.

Başlamadan önce mevcut dosya yapısını tara ve bana ne bulduğunu söyle.

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
