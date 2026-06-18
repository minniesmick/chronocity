import type { CityId, CityMeta } from "@/types";

/**
 * Şehir kayıt defteri. `hasBuildingData` tek doğruluk kaynağı:
 * public/cities/{id}/buildings.geojson mevcutsa true.
 * Veri geldikçe flag açılır; kapalıyken şehir seçilince no-op.
 */
export const CITIES: Record<CityId, CityMeta> = {
  "new-york": {
    id: "new-york",
    name: "New York",
    country: "USA",
    flag: "🇺🇸",
    color: "#3b82f6",
    center: [-73.988, 40.748], // Midtown/Flatiron — işlenmiş veri bbox merkezi
    hasBuildingData: true,
    stats: {
      population: "8.26M",
      founded: "1624",
      milestones: [
        "1898 — Beş ilçe birleşti",
        "1931 — Empire State açıldı",
        "2001 — 11 Eylül",
      ],
    },
  },
  istanbul: {
    id: "istanbul",
    name: "İstanbul",
    country: "Türkiye",
    flag: "🇹🇷",
    color: "#f59e0b",
    center: [28.978, 41.008],
    hasBuildingData: false,
  },
  chicago: {
    id: "chicago",
    name: "Chicago",
    country: "USA",
    flag: "🇺🇸",
    color: "#8b5cf6",
    center: [-87.63, 41.882],
    hasBuildingData: false,
  },
  berlin: {
    id: "berlin",
    name: "Berlin",
    country: "Deutschland",
    flag: "🇩🇪",
    color: "#10b981",
    center: [13.405, 52.52],
    hasBuildingData: false,
  },
  vienna: {
    id: "vienna",
    name: "Wien",
    country: "Österreich",
    flag: "🇦🇹",
    color: "#ef4444",
    center: [16.373, 48.208],
    hasBuildingData: false,
  },
};

export const CITY_LIST: CityMeta[] = Object.values(CITIES);

export const AVAILABLE_CITIES: CityMeta[] = CITY_LIST.filter(
  (c) => c.hasBuildingData,
);
