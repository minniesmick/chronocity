import type { CityEvent } from "@/types";
import { tFromYear } from "@/lib/time";

interface Props {
  events: CityEvent[];
  currentYear: number;
  onHover: (event: CityEvent | null) => void;
}

const TYPE_CLASS: Record<CityEvent["type"], string> = {
  positive: "event-marker--positive",
  negative: "event-marker--negative",
  neutral:  "event-marker--neutral",
};

function eventYear(e: CityEvent): number {
  return parseInt(e.date.slice(0, 4), 10);
}

export default function EventMarker({ events, currentYear, onHover }: Props) {
  return (
    <>
      {events.map((ev) => {
        const year = eventYear(ev);
        const dist = Math.abs(currentYear - year);
        // >20 yıl uzakta: gizli; 10-20: yarı saydamlık; <10: tam görünür
        const opacity = dist > 20 ? 0 : dist > 10 ? 0.4 : 1;
        const isPulsing = dist <= 2;

        return (
          <div
            key={ev.date + ev.title}
            className={`event-marker ${TYPE_CLASS[ev.type]}${isPulsing ? " event-marker--pulse" : ""}`}
            style={{
              left: `${tFromYear(year) * 100}%`,
              opacity,
              transition: "opacity 0.4s ease",
            }}
            title={`${year} — ${ev.title}`}
            onMouseEnter={() => onHover(ev)}
            onMouseLeave={() => onHover(null)}
          />
        );
      })}
    </>
  );
}
