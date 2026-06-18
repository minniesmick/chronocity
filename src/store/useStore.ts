import { create } from "zustand";
import type { CityId, EraId, CityEvent } from "@/types";

/**
 * ChronoCity global state. Tüm duyusal katmanlar (shader, audio, particle)
 * `t` parametresinden beslenir — tek senkronizasyon kaynağı.
 */
interface ChronoState {
  t: number; // 0.0–1.0 zaman parametresi
  activeCity: CityId | null;
  era: EraId;
  isDayMode: boolean;
  isPlaying: boolean; // timeline otomatik akıyor mu
  activeEvent: CityEvent | null;
  audioReady: boolean; // Web Audio API user-gesture sonrası

  setT: (t: number) => void;
  setActiveCity: (city: CityId | null) => void;
  setEra: (era: EraId) => void;
  toggleDayMode: () => void;
  setPlaying: (playing: boolean) => void;
  setActiveEvent: (event: CityEvent | null) => void;
  setAudioReady: (ready: boolean) => void;
}

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);

export const useStore = create<ChronoState>((set) => ({
  t: 1, // varsayılan: günümüz (2026), tam skyline. Geri sürünce tarih açılır.
  activeCity: null,
  era: "modern",
  isDayMode: true,
  isPlaying: false,
  activeEvent: null,
  audioReady: false,

  setT: (t) => set({ t: clamp01(t) }),
  setActiveCity: (activeCity) => set({ activeCity }),
  setEra: (era) => set({ era }),
  toggleDayMode: () => set((s) => ({ isDayMode: !s.isDayMode })),
  setPlaying: (isPlaying) => set({ isPlaying }),
  setActiveEvent: (activeEvent) => set({ activeEvent }),
  setAudioReady: (audioReady) => set({ audioReady }),
}));

// Dev: konsoldan/otomasyondan state sürmek için (deterministik test).
if (import.meta.env.DEV) {
  (window as unknown as { useStore: typeof useStore }).useStore = useStore;
}
