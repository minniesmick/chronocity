import { useEffect, useMemo, useRef, useState } from "react";
import DeckGL from "@deck.gl/react";
import { GeoJsonLayer } from "@deck.gl/layers";
import {
  AmbientLight,
  DirectionalLight,
  LightingEffect,
  type MapViewState,
} from "@deck.gl/core";
import type { Feature, Geometry } from "geojson";
import type { CityId, BuildingProperties } from "@/types";
import { CITIES } from "@/data/cities";
import { useCityBuildings } from "@/hooks/useCityBuildings";
import { useStore } from "@/store/useStore";
import { yearFromT } from "@/lib/time";
import { colorByEra, colorUndated } from "@/lib/buildingColors";

type BFeature = Feature<Geometry, BuildingProperties>;

const dayLighting = new LightingEffect({
  ambient: new AmbientLight({ color: [255, 245, 230], intensity: 1.1 }),
  sun: new DirectionalLight({
    color: [255, 220, 180],
    intensity: 1.4,
    direction: [-1, -3, -1],
  }),
});

const nightLighting = new LightingEffect({
  ambient: new AmbientLight({ color: [150, 170, 220], intensity: 0.5 }),
  sun: new DirectionalLight({
    color: [255, 200, 150],
    intensity: 0.7,
    direction: [-1, -3, -1],
  }),
});

const isBuilt = (f: BFeature, year: number): boolean => {
  const y = f.properties.construction_year;
  return y == null || y <= year;
};

export default function MapCanvas({ city }: { city: CityId }) {
  const { data, loading, error } = useCityBuildings(city);
  const t = useStore((s) => s.t);
  const isDayMode = useStore((s) => s.isDayMode);
  const currentYear = yearFromT(t);

  // Pulse animasyonu için ~20fps RAF sayacı
  const [frame, setFrame] = useState(0);
  const rafRef = useRef<number>(0);
  useEffect(() => {
    let last = 0;
    const tick = (now: number) => {
      if (now - last > 50) {
        last = now;
        setFrame((f) => f + 1);
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  const center = CITIES[city].center;
  const initialViewState: MapViewState = {
    longitude: center[0],
    latitude: center[1],
    zoom: 14.5,
    pitch: 50,
    bearing: -20,
    maxPitch: 75,
  };

  const layers = useMemo(() => {
    if (!data) return [];
    return [
      new GeoJsonLayer<BuildingProperties>({
        id: `buildings-${city}`,
        data,
        extruded: true,
        wireframe: false,
        getElevation: (f: BFeature) =>
          isBuilt(f, currentYear) ? f.properties.height : 0,
        getFillColor: (f: BFeature) => {
          if (!isBuilt(f, currentYear)) return [0, 0, 0, 0];
          const year = f.properties.construction_year;
          if (year == null) return colorUndated(frame, !isDayMode);
          return colorByEra(year, !isDayMode);
        },
        material: {
          ambient: 0.5,
          diffuse: 0.6,
          shininess: 32,
          specularColor: [60, 50, 40],
        },
        pickable: true,
        transitions: { getElevation: 400, getFillColor: 400 },
        updateTriggers: {
          getElevation: currentYear,
          getFillColor: [currentYear, isDayMode, frame],
        },
      }),
    ];
  }, [data, city, currentYear, isDayMode, frame]);

  return (
    <div className="map-canvas">
      <DeckGL
        initialViewState={initialViewState}
        controller={true}
        effects={[isDayMode ? dayLighting : nightLighting]}
        layers={layers}
        style={{ background: "transparent" }}
      />
      {loading && <div className="map-canvas__status">binalar yükleniyor…</div>}
      {error && (
        <div className="map-canvas__status map-canvas__status--err">
          veri hatası: {error}
        </div>
      )}
    </div>
  );
}
