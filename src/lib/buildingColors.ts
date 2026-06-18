// Bina renk rampası — tekno-sinematik amber/ember.
// Yükseklik arttıkça koyu ember → parlak amber.
// (Sprint 1b'de bu mantık GLSL uTime shader'ına taşınacak; şimdilik JS-side
//  data-driven, `t` değişince updateTriggers ile yeniden hesaplanır.)

type RGB = [number, number, number];

const EMBER: RGB = [120, 53, 15]; // koyu, kısa binalar
const AMBER: RGB = [251, 191, 36]; // parlak, yüksek binalar
const HEIGHT_NORM = 250; // metre — normalizasyon tavanı (Empire State ~381m clamp)

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;

/**
 * Yüksekliğe göre amber gradyan. alpha sabit opak.
 * night=true → kısa binalar kararır, yüksekler parlak kalır (gece şehir ışıkları hissi).
 */
export function colorByHeight(
  height: number,
  night = false,
): [number, number, number, number] {
  const k = clamp01(height / HEIGHT_NORM);
  const mul = night ? 0.5 + 0.5 * k : 1;
  return [
    Math.round(lerp(EMBER[0], AMBER[0], k) * mul),
    Math.round(lerp(EMBER[1], AMBER[1], k) * mul),
    Math.round(lerp(EMBER[2], AMBER[2], k) * mul),
    230,
  ];
}
