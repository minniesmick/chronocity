import { useEffect, useState } from "react";
import type { CityId, BuildingProperties } from "@/types";
import { CITIES } from "@/data/cities";

type FC = GeoJSON.FeatureCollection<GeoJSON.Geometry, BuildingProperties>;

interface State {
  data: FC | null;
  loading: boolean;
  error: string | null;
}

/**
 * Aktif şehrin buildings.geojson'ını lazy yükler.
 * Verisi olmayan şehir (hasBuildingData=false) → no-op, yükleme yok.
 */
export function useCityBuildings(city: CityId | null): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!city || !CITIES[city].hasBuildingData) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    let cancelled = false;
    setState({ data: null, loading: true, error: null });

    fetch(`/cities/${city}/buildings.geojson`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: FC) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((e: Error) => {
        if (!cancelled)
          setState({ data: null, loading: false, error: e.message });
      });

    return () => {
      cancelled = true;
    };
  }, [city]);

  return state;
}
