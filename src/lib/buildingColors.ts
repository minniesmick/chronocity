type RGBA = [number, number, number, number];

// Era renk skalasi — donem atmosferi
const ERA_BANDS: Array<{ until: number; day: [number, number, number] }> = [
  { until: 1870, day: [180, 150, 100] }, // taş/barok
  { until: 1918, day: [190, 120,  80] }, // Grunderzeit tuğla
  { until: 1945, day: [200, 165,  60] }, // Art Deco altın
  { until: 1970, day: [140, 150, 160] }, // beton/brutalzim
  { until: 1990, day: [175, 175, 155] }, // prefab bej
  { until: 2010, day: [130, 175, 150] }, // cam/celik
  { until: 9999, day: [100, 170, 215] }, // modern cam-mavi
];

/**
 * Yapım yılına göre dönem rengi.
 * night=true → 55% karartma.
 */
export function colorByEra(year: number, night = false): RGBA {
  const band = ERA_BANDS.find((b) => year < b.until) ?? ERA_BANDS[ERA_BANDS.length - 1];
  const mul = night ? 0.55 : 1.0;
  return [
    Math.round(band.day[0] * mul),
    Math.round(band.day[1] * mul),
    Math.round(band.day[2] * mul),
    220,
  ];
}

/**
 * Tarihi belirsiz (construction_year=null) binalara nefes efekti rengi.
 * frame: RAF sayacından gelen int — Math.sin ile pulse hesaplanır.
 */
export function colorUndated(frame: number, night = false): RGBA {
  const pulse = 0.5 + 0.5 * Math.sin(frame * 0.08);
  const base = night ? 50 : 95;
  const v = Math.round(base + 30 * pulse);
  return [v, v + 10, v + 30, Math.round(55 + 40 * pulse)];
}
