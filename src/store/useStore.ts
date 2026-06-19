import { create } from "zustand";
import type { CityId, EraId, CityEvent, BuildingProperties } from "@/types";

export interface ActiveBuilding {
  properties: BuildingProperties;
  x: number; // viewport px
  y: number;
}

interface ChronoState {
  t: number;
  activeCity: CityId | null;
  era: EraId;
  isDayMode: boolean;
  isPlaying: boolean;
  activeEvent: CityEvent | null;
  activeBuilding: ActiveBuilding | null;
  audioReady: boolean;

  setT: (t: number) => void;
  setActiveCity: (city: CityId | null) => void;
  setEra: (era: EraId) => void;
  toggleDayMode: () => void;
  setPlaying: (playing: boolean) => void;
  setActiveEvent: (event: CityEvent | null) => void;
  setActiveBuilding: (b: ActiveBuilding | null) => void;
  setAudioReady: (ready: boolean) => void;
}

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);

export const useStore = create<ChronoState>((set) => ({
  t: 1,
  activeCity: null,
  era: "modern",
  isDayMode: true,
  isPlaying: false,
  activeEvent: null,
  activeBuilding: null,
  audioReady: false,

  setT: (t) => set({ t: clamp01(t) }),
  setActiveCity: (activeCity) => set({ activeCity }),
  setEra: (era) => set({ era }),
  toggleDayMode: () => set((s) => ({ isDayMode: !s.isDayMode })),
  setPlaying: (isPlaying) => set({ isPlaying }),
  setActiveEvent: (activeEvent) => set({ activeEvent }),
  setActiveBuilding: (activeBuilding) => set({ activeBuilding }),
  setAudioReady: (audioReady) => set({ audioReady }),
}));

if (import.meta.env.DEV) {
  (window as unknown as { useStore: typeof useStore }).useStore = useStore;
}
