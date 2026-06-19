import { useState, useEffect } from "react";
import { useStore } from "@/store/useStore";
import type { CityEvent } from "@/types";

export function useCityEvents(): CityEvent[] {
  const activeCity = useStore((s) => s.activeCity);
  const [events, setEvents] = useState<CityEvent[]>([]);

  useEffect(() => {
    if (!activeCity) { setEvents([]); return; }
    fetch(`/cities/${activeCity}/events/info.json`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setEvents)
      .catch(() => setEvents([]));
  }, [activeCity]);

  return events;
}
