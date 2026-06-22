import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import DeckGL from "@deck.gl/react";
import { BitmapLayer, GeoJsonLayer } from "@deck.gl/layers";
import { TileLayer } from "@deck.gl/geo-layers";
import {
  AmbientLight,
  DirectionalLight,
  FlyToInterpolator,
  LightingEffect,
  type MapViewState,
} from "@deck.gl/core";
import type { Feature, Geometry } from "geojson";
import type { CityId, BuildingProperties } from "@/types";
import { CITIES } from "@/data/cities";
import { useCityBuildings } from "@/hooks/useCityBuildings";
import { useStore } from "@/store/useStore";
import type { ActiveBuilding } from "@/store/useStore";
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
  const cameraResetKey = useStore((s) => s.cameraResetKey);
  const setActiveBuilding = useStore((s) => s.setActiveBuilding);
  const setCurrentZoom = useStore((s) => s.setCurrentZoom);
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

  // FlyTo: uncontrolled → controlled viewState
  const center = CITIES[city].center;
  const [viewState, setViewState] = useState<MapViewState>({
    longitude: center[0],
    latitude: center[1],
    zoom: 5,
    pitch: 20,
    bearing: 0,
    minZoom: 12,
    maxPitch: 75,
  });

  // Mount'ta şehre uç — loading screen kapanmadan başlar, kapanınca reveal edilir
  useEffect(() => {
    const id = setTimeout(() => {
      setViewState({
        longitude: center[0],
        latitude: center[1],
        zoom: 14.5,
        pitch: 50,
        bearing: -20,
        minZoom: 12,
        maxPitch: 75,
        transitionDuration: 2200,
        transitionInterpolator: new FlyToInterpolator({ speed: 1.4 }),
      });
    }, 300);
    return () => clearTimeout(id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // sadece mount'ta — city prop değişmez (unmount → remount)

  // Kamera sıfırla — store'dan tetiklenir
  useEffect(() => {
    if (cameraResetKey === 0) return;
    setViewState({
      longitude: center[0],
      latitude: center[1],
      zoom: 14.5,
      pitch: 50,
      bearing: -20,
      minZoom: 12,
      maxPitch: 75,
      transitionDuration: 900,
      transitionInterpolator: new FlyToInterpolator({ speed: 1.6 }),
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cameraResetKey]);

  const cityBbox = CITIES[city].bbox;

  // Zoom sınır göstergesi
  const [zoomHint, setZoomHint] = useState<'min' | 'max' | null>(null);
  const zoomHintTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const prevZoomRef = useRef(viewState.zoom);

  const triggerZoomHint = (type: 'min' | 'max') => {
    clearTimeout(zoomHintTimer.current);
    setZoomHint(type);
    zoomHintTimer.current = setTimeout(() => setZoomHint(null), 1600);
  };

  const layers = useMemo(() => {
    const satelliteLayer = new TileLayer({
      id: "satellite",
      data: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      minZoom: 0,
      maxZoom: 19,
      tileSize: 256,
      extent: cityBbox,  // only load tiles covering this city's bbox
      opacity: isDayMode ? 0.80 : 0.45,
      renderSubLayers: (props) => {
        const { boundingBox } = props.tile;
        return new BitmapLayer({
          ...props,
          data: undefined,
          image: props.data,
          bounds: [
            boundingBox[0][0],
            boundingBox[0][1],
            boundingBox[1][0],
            boundingBox[1][1],
          ],
        });
      },
    });

    if (!data) return [satelliteLayer];
    return [
      satelliteLayer,
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
          ambient: 0.72,
          diffuse: 0.45,
          shininess: 32,
          specularColor: [60, 50, 40],
        },
        pickable: true,
        onClick: (info) => {
          if (info.object) {
            setActiveBuilding({
              properties: info.object.properties,
              x: info.x,
              y: info.y,
            } as ActiveBuilding);
          } else {
            setActiveBuilding(null);
          }
        },
        transitions: { getElevation: 400, getFillColor: 400 },
        updateTriggers: {
          getElevation: currentYear,
          getFillColor: [currentYear, isDayMode, frame],
        },
      }),
    ];
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, city, currentYear, isDayMode, frame, cityBbox]);

  return (
    <div className="map-canvas">
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: vs }) => {
          const newVs = vs as MapViewState;
          const newZoom = newVs.zoom ?? 0;
          const prevZoom = prevZoomRef.current;
          prevZoomRef.current = newZoom;
          if (newZoom <= 12 && prevZoom > 12) triggerZoomHint('min');
          if (newZoom >= 18.8 && prevZoom < 18.8) triggerZoomHint('max');
          setCurrentZoom(newZoom);
          setViewState(newVs);
        }}
        controller={true}
        effects={[isDayMode ? dayLighting : nightLighting]}
        layers={layers}
        style={{ background: "#0a0a0f" }}
        onClick={(info) => {
          if (!info.object) setActiveBuilding(null);
        }}
      />
      <AnimatePresence>
        {zoomHint && (
          <motion.div
            className="map-zoom-hint"
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.95 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
          >
            {zoomHint === 'min'
              ? <><span className="map-zoom-hint__icon">⊖</span> Uzaklaştırma sınırı</>
              : <><span className="map-zoom-hint__icon">⊕</span> Yakınlaştırma sınırı</>
            }
          </motion.div>
        )}
      </AnimatePresence>

      {loading && <div className="map-canvas__status">binalar yükleniyor…</div>}
      {error && (
        <div className="map-canvas__status map-canvas__status--err">
          veri hatası: {error}
        </div>
      )}
    </div>
  );
}
