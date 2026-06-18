// Zaman parametresi `t` (0–1) ↔ takvim yılı eşlemesi.
// NYC veri aralığı: construction_year 1800–2026.
// (Sonra şehir başına aralık CityMeta'ya taşınabilir.)

export const YEAR_MIN = 1800;
export const YEAR_MAX = 2026;

export const yearFromT = (t: number): number =>
  Math.round(YEAR_MIN + t * (YEAR_MAX - YEAR_MIN));

export const tFromYear = (year: number): number =>
  (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN);
