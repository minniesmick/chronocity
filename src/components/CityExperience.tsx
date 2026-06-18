import { useStore } from "@/store/useStore";
import { CITIES } from "@/data/cities";
import type { CityId } from "@/types";
import MapCanvas from "@/components/MapCanvas";
import DevTimeScrubber from "@/components/DevTimeScrubber";
import DayNightToggle from "@/components/DayNightToggle";
import "@/components/sprint1.css";

/**
 * SPRINT 1 ana sahne kabuğu. MapCanvas (3D bina) + geçici scrubber + geri.
 * SPRINT 2'de CityLoadingScreen → MainExperience router'ı bunu sarmalayacak.
 */
export default function CityExperience({ city }: { city: CityId }) {
  const setActiveCity = useStore((s) => s.setActiveCity);
  const isDayMode = useStore((s) => s.isDayMode);
  const meta = CITIES[city];

  return (
    <div className="city-exp" data-day={isDayMode}>
      <MapCanvas city={city} />

      <header className="city-exp__top">
        <button
          className="city-exp__back"
          onClick={() => setActiveCity(null)}
          aria-label="Şehir seçimine dön"
        >
          ← geri
        </button>
        <span className="city-exp__name" style={{ "--c": meta.color } as React.CSSProperties}>
          <span className="city-exp__dot" /> {meta.name}
        </span>
        <span className="city-exp__spacer" />
        <DayNightToggle />
      </header>

      <DevTimeScrubber />
    </div>
  );
}
