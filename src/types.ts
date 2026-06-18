// ChronoCity — paylaşılan tipler

export type CityId = "istanbul" | "new-york" | "chicago" | "berlin" | "vienna";

export type EraId = "1960s" | "1980s" | "2000s" | "modern";

export type EventType = "positive" | "negative" | "neutral";

export interface CityEvent {
  date: string; // ISO "YYYY-MM-DD"
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
  flag: string; // emoji bayrak
  color: string; // globe noktası rengi (tokens.css ile eşleşir)
  center: [number, number]; // [lon, lat] — harita default merkezi
  /** Bu şehrin işlenmiş buildings.geojson verisi mevcut mu?
   *  false → şehir seçilince no-op (veri toplama sonra). */
  hasBuildingData: boolean;
  /** Loading ekranı için kısa istatistikler (typewriter). */
  stats?: {
    population: string;
    founded: string;
    milestones: string[];
  };
}

// Yükseklik + inşa yılı taşıyan bina footprint'i (deck.gl GeoJsonLayer)
export interface BuildingProperties {
  height: number; // metre
  construction_year: number | null;
  name: string | null;
}
