// Zaman parametresi `t` (0–1) ↔ takvim yılı eşlemesi.
// NYC veri aralığı: construction_year 1800–2026.
// (Sonra şehir başına aralık CityMeta'ya taşınabilir.)

import type { EraId } from "@/types";

export const YEAR_MIN = 1800;
export const YEAR_MAX = 2026;

export const yearFromT = (t: number): number =>
  Math.round(YEAR_MIN + t * (YEAR_MAX - YEAR_MIN));

export const tFromYear = (year: number): number =>
  Math.max(0, Math.min(1, (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN)));

// Yıl → müzik era eşlemesi
export const eraFromYear = (year: number): EraId => {
  if (year < 1970) return "1960s";
  if (year < 1990) return "1980s";
  if (year < 2010) return "2000s";
  return "modern";
};
