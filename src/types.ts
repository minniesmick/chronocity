// ChronoCity — paylaşılan tipler

export type CityId =
  | "istanbul"
  | "new-york"
  | "chicago"
  | "berlin"
  | "vienna"
  | "paris"
  | "london"
  | "barcelona"
  | "madrid"
  | "tokyo"
  | "moscow";

export type EraId = "1960s" | "1980s" | "2000s" | "modern";

export type EventType = "positive" | "negative" | "neutral";

export interface CityEvent {
  date: string;
  title: string;
  shortDesc: string;
  type: EventType;
  category: string;
  coordinates: [number, number]; // [lat, lon]
  wikiSlug?: string;
}

export interface CityMeta {
  id: CityId;
  name: string;
  country: string;
  flag: string;        // emoji bayrak (fallback)
  countryCode: string; // ISO 3166-1 alpha-2, küçük harf — flag-icons için (fi fi-{code})
  color: string;
  center: [number, number]; // [lon, lat]
  bbox: [number, number, number, number]; // [minLon, minLat, maxLon, maxLat] — TileLayer extent + zoom bounds
  hasBuildingData: boolean;
  stats?: {
    population: string;
    founded: string;
    milestones: string[];
  };
}

export interface BuildingProperties {
  height: number;
  construction_year: number | null;
  name: string | null;
}
