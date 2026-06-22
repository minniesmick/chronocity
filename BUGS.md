# ChronoCity — Bilinen Bug'lar & Çözümler

## [ÇÖZÜLDÜ] Globe → City navigasyonu çalışmıyor

**Tarih:** 2026-06-22  
**Dosya:** `src/components/GlobeSelector.tsx`, `src/components/sprint2.css`

### Belirtiler
- City dot'a hover → kart görünüyor ✓
- Dot'a tıklayınca kart expand olmuyor / FLY TO butonu çıkmıyor ✗
- Çok hassas: tam noktanın merkezine basmak gerekiyor

### Kök Nedenler (3 ayrı bug)

**Bug 1 — RAF drag sırasında hoveredId sıfırlanıyor**  
`onDown` tetiklenince `dragging = true` oluyor. RAF döngüsünde:
```js
const hits = dragging ? [] : raycaster.intersectObjects(dotMeshes);
```
`dragging=true` → `hits=[]` → `hoveredId=null` → `onUp` çalışınca hedef şehir bulunamıyor.  
**Fix:** `pointerdown`'da `clickedId = hoveredId` ile değeri sakla, `onUp`'ta `hoveredId` yerine `clickedId` kullan.

**Bug 2 — Canvas click outer div'e bubble edip closeSelected çağırıyor**  
`onUp` → şehir seçilir → `click` event canvas'tan outer `motion.div`'e bubble eder → `onClick={closeSelected}` → anında deselect.  
**Fix:** `<canvas onClick={(e) => e.stopPropagation()} />`

**Bug 3 — Hover bitince pointer-events anında none oluyor**  
Fare dot'tan kart div'ine geçerken RAF bir frame içinde `card.style.pointerEvents = 'none'` setliyor. Kart visible ama tıklanamıyor.  
**Fix:** CSS transition-delay ile `pointer-events: none` 280ms gecikmeli devreye giriyor. RAF'ta inline style yerine CSS class kullan (`city-card--visible`).

```css
.city-card {
  pointer-events: none;
  transition: pointer-events 0s linear 0.28s; /* gecikmeli none */
}
.city-card--visible {
  pointer-events: auto;
  transition: pointer-events 0s linear 0s; /* anında auto */
}
```

### Öğrenilen Dersler
- Three.js raycaster + native pointer events karışınca timing hassas — state'i `pointerdown` anında yakala
- React synthetic `onClick` ile native `addEventListener` aynı anda kullanılınca click bubbling race condition oluşur
- RAF'ta inline `style.pointerEvents` → CSS geçişleri override eder; class kullan
