import { useState, useEffect } from "react";
import { useStore } from "@/store/useStore";
import type { CityEvent } from "@/types";

// Module-level cache — useCityBuildings ile aynı desen; şehre her girişte refetch yok
const cache = new Map<string, CityEvent[]>();

export function useCityEvents(): CityEvent[] {
  const activeCity = useStore((s) => s.activeCity);
  const [events, setEvents] = useState<CityEvent[]>(() =>
    activeCity ? cache.get(activeCity) ?? [] : [],
  );

  useEffect(() => {
    if (!activeCity) { setEvents([]); return; }
    if (cache.has(activeCity)) { setEvents(cache.get(activeCity)!); return; }

    let cancelled = false;
    fetch(`/cities/${activeCity}/events/info.json`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data: CityEvent[]) => {
        if (cancelled) return;
        cache.set(activeCity, data);
        setEvents(data);
      })
      .catch(() => { if (!cancelled) setEvents([]); });

    return () => { cancelled = true; };
  }, [activeCity]);

  return events;
}
