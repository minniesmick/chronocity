import { useEffect, useState } from "react";
import type { CityId, BuildingProperties } from "@/types";
import { CITIES } from "@/data/cities";

type FC = GeoJSON.FeatureCollection<GeoJSON.Geometry, BuildingProperties>;

interface State {
  data: FC | null;
  loading: boolean;
  error: string | null;
}

// Module-level cache — sayfa yenilenene kadar yaşar, re-fetch yok
const cache = new Map<CityId, FC>();

/**
 * Aktif şehrin buildings.geojson'ını lazy yükler.
 * İkinci ziyarette cache'den döner (fetch yok).
 * Yeni şehir yüklenirken eski veri tutulur → flash of empty map yok.
 */
export function useCityBuildings(city: CityId | null): State {
  const [state, setState] = useState<State>(() => {
    if (city && cache.has(city)) {
      return { data: cache.get(city)!, loading: false, error: null };
    }
    return { data: null, loading: !!city && !!CITIES[city]?.hasBuildingData, error: null };
  });

  useEffect(() => {
    if (!city || !CITIES[city].hasBuildingData) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    // Cache hit — anında render, fetch yok
    if (cache.has(city)) {
      setState({ data: cache.get(city)!, loading: false, error: null });
      return;
    }

    let cancelled = false;
    // Eski veri varsa koru (loading:true ama data:mevcut) — flash yok
    setState((prev) => ({ ...prev, loading: true, error: null }));

    fetch(`/cities/${city}/buildings.geojson`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: FC) => {
        if (cancelled) return;
        cache.set(city, data);
        setState({ data, loading: false, error: null });
      })
      .catch((e: Error) => {
        if (!cancelled)
          setState((prev) => ({ ...prev, loading: false, error: e.message }));
      });

    return () => { cancelled = true; };
  }, [city]);

  return state;
}
