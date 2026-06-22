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
    countryCode: "us",
    color: "#38bdf8",
    center: [-73.988, 40.748],
    bbox: [-74.02, 40.71, -73.94, 40.79],
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
    countryCode: "tr",
    color: "#f59e0b",
    center: [28.965, 41.013],
    bbox: [28.92, 40.97, 29.01, 41.06],
    hasBuildingData: true,
    stats: {
      population: "15.9M",
      founded: "660 BC",
      milestones: [
        "330 — Konstantinopolis kuruldu",
        "1453 — Fatih Sultan Mehmet fethetti",
        "1973 — Boğaz Köprüsü açıldı",
      ],
    },
  },
  chicago: {
    id: "chicago",
    name: "Chicago",
    country: "USA",
    flag: "🇺🇸",
    countryCode: "us",
    color: "#a3e635",
    center: [-87.628, 41.878],
    bbox: [-87.67, 41.84, -87.58, 41.92],
    hasBuildingData: true,
    stats: {
      population: "2.7M",
      founded: "1837",
      milestones: [
        "1871 — Büyük yangın şehri yaktı",
        "1885 — Dünyanın ilk gökdeleni",
        "1893 — Dünya Fuarı",
      ],
    },
  },
  berlin: {
    id: "berlin",
    name: "Berlin",
    country: "Deutschland",
    flag: "🇩🇪",
    countryCode: "de",
    color: "#4ade80",
    center: [13.405, 52.52],
    bbox: [13.36, 52.49, 13.45, 52.55],
    hasBuildingData: true,
    stats: {
      population: "3.7M",
      founded: "1237",
      milestones: [
        "1871 — Alman İmparatorluğu başkenti",
        "1961 — Duvar inşa edildi",
        "1989 — Duvar yıkıldı",
      ],
    },
  },
  vienna: {
    id: "vienna",
    name: "Wien",
    country: "Österreich",
    flag: "🇦🇹",
    countryCode: "at",
    color: "#8b5cf6",
    center: [16.373, 48.208],
    bbox: [16.33, 48.17, 16.42, 48.25],
    hasBuildingData: true,
    stats: {
      population: "1.9M",
      founded: "~500 BC",
      milestones: [
        "1683 — Osmanlı kuşatması püskürtüldü",
        "1814 — Viyana Kongresi",
        "1945 — Sovyetler işgal etti",
      ],
    },
  },
  paris: {
    id: "paris",
    name: "Paris",
    country: "France",
    flag: "🇫🇷",
    countryCode: "fr",
    color: "#e879f9",
    center: [2.352, 48.856],
    bbox: [2.30, 48.82, 2.41, 48.90],
    hasBuildingData: true,
    stats: {
      population: "2.1M",
      founded: "~250 BC",
      milestones: [
        "1789 — Fransız Devrimi",
        "1853 — Haussmann Paris'i yeniden inşa etti",
        "1889 — Eyfel Kulesi açıldı",
      ],
    },
  },
  london: {
    id: "london",
    name: "London",
    country: "United Kingdom",
    flag: "🇬🇧",
    countryCode: "gb",
    color: "#14b8a6",
    center: [-0.08, 51.505],
    bbox: [-0.14, 51.46, -0.01, 51.55],
    hasBuildingData: true,
    stats: {
      population: "9.0M",
      founded: "43 AD",
      milestones: [
        "1666 — Büyük Londra Yangını",
        "1863 — Dünya'nın ilk metrosu",
        "2012 — Olimpiyat Oyunları",
      ],
    },
  },
  barcelona: {
    id: "barcelona",
    name: "Barcelona",
    country: "España",
    flag: "🇪🇸",
    countryCode: "es",
    color: "#6366f1",
    center: [2.164, 41.389],
    bbox: [2.12, 41.35, 2.22, 41.43],
    hasBuildingData: true,
    stats: {
      population: "1.6M",
      founded: "~15 BC",
      milestones: [
        "1859 — Eixample grid planı",
        "1882 — Sagrada Família başladı",
        "1992 — Olimpiyat Oyunları",
      ],
    },
  },
  madrid: {
    id: "madrid",
    name: "Madrid",
    country: "España",
    flag: "🇪🇸",
    countryCode: "es",
    color: "#f43f5e",
    center: [-3.695, 40.416],
    bbox: [-3.74, 40.37, -3.64, 40.46],
    hasBuildingData: true,
    stats: {
      population: "3.3M",
      founded: "865 AD",
      milestones: [
        "1561 — İspanya başkenti oldu",
        "1819 — Prado Müzesi açıldı",
        "1992 — Avrupa Kültür Başkenti",
      ],
    },
  },
  tokyo: {
    id: "tokyo",
    name: "Tokyo",
    country: "Japan",
    flag: "🇯🇵",
    countryCode: "jp",
    color: "#f472b6",
    center: [139.745, 35.69],
    bbox: [139.70, 35.65, 139.80, 35.73],
    hasBuildingData: true,
    stats: {
      population: "13.9M",
      founded: "1457",
      milestones: [
        "1869 — İmparatorluk başkenti",
        "1923 — Büyük Kanto depremi",
        "1964 — Olimpiyat Oyunları",
      ],
    },
  },
  moscow: {
    id: "moscow",
    name: "Moskva",
    country: "Russia",
    flag: "🇷🇺",
    countryCode: "ru",
    color: "#e2e8f0",
    center: [37.617, 55.755],
    bbox: [37.56, 55.72, 37.68, 55.79],
    hasBuildingData: true,
    stats: {
      population: "12.5M",
      founded: "1147",
      milestones: [
        "1812 — Napolyon işgali",
        "1935 — Stalin yeniden yapılandırdı",
        "1991 — SSCB çöküşü",
      ],
    },
  },
};

export const CITY_LIST: CityMeta[] = Object.values(CITIES);

export const AVAILABLE_CITIES: CityMeta[] = CITY_LIST.filter(
  (c) => c.hasBuildingData,
);
