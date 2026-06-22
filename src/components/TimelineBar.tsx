import { useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/store/useStore";
import { yearFromT, tFromYear, eraFromYear, YEAR_MIN, YEAR_MAX } from "@/lib/time";
import { useCityEvents } from "@/hooks/useCityEvents";
import EventMarker from "@/components/EventMarker";
import { ERA_ID_COLORS } from "@/lib/eraColors";
import type { EraId } from "@/types";

const ERA_TICKS = [1800, 1870, 1918, 1945, 1980, 2000, 2010, 2026];
const YEAR_RANGE = YEAR_MAX - YEAR_MIN;
const MS_PER_YEAR = 180;

// Müzik era etiketleri (Türkçe)
// Dosya yolu: /public/cities/{cityId}/music/{eraId}.mp3
const ERA_LABELS: Record<EraId, string> = {
  "1960s": "60'lar",
  "1980s": "80'ler",
  "2000s": "2000'ler",
  modern: "Modern",
};

const ERA_ORDER: EraId[] = ["1960s", "1980s", "2000s", "modern"];

export default function TimelineBar() {
  const t = useStore((s) => s.t);
  const isPlaying = useStore((s) => s.isPlaying);
  const era = useStore((s) => s.era);
  const setT = useStore((s) => s.setT);
  const setPlaying = useStore((s) => s.setPlaying);
  const setEra = useStore((s) => s.setEra);

  const currentYear = yearFromT(t);
  const events = useCityEvents();

  const setActiveEvent = useStore((s) => s.setActiveEvent);

  // --- Auto-play ---
  useEffect(() => {
    if (!isPlaying) return;
    const iv = setInterval(() => {
      const cur = useStore.getState().t;
      if (cur >= 1) {
        setPlaying(false);
      } else {
        const next = Math.min(cur + 1 / YEAR_RANGE, 1);
        setT(next);
        setEra(eraFromYear(yearFromT(next)));
      }
    }, MS_PER_YEAR);
    return () => clearInterval(iv);
  }, [isPlaying, setT, setPlaying, setEra]);

  // --- Klavye ---
  const onKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;
      const step = e.shiftKey ? 10 : 1;
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        const yr = currentYear - step;
        setT(tFromYear(yr));
        setEra(eraFromYear(yr));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        const yr = currentYear + step;
        setT(tFromYear(yr));
        setEra(eraFromYear(yr));
      } else if (e.key === " ") {
        e.preventDefault();
        setPlaying(!isPlaying);
      }
    },
    [currentYear, isPlaying, setT, setPlaying, setEra],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKey]);

  return (
    <div
      className="timeline"
      role="region"
      aria-label="Zaman çizelgesi"
    >
      {/* Sol: play/pause + yıl */}
      <div className="timeline__left">
        <button
          className="timeline__play"
          onClick={() => setPlaying(!isPlaying)}
          aria-label={isPlaying ? "Durdur" : "Oynat"}
        >
          {isPlaying ? "⏸" : "▶"}
        </button>
        <AnimatePresence mode="popLayout">
          <motion.span
            key={currentYear}
            className="timeline__year"
            aria-live="polite"
            initial={{ opacity: 0.5, filter: "blur(4px)" }}
            animate={{ opacity: 1, filter: "blur(0px)" }}
            transition={{ duration: 0.1, ease: "easeOut" }}
          >
            {currentYear}
          </motion.span>
        </AnimatePresence>
      </div>

      {/* Merkez: track-area (event noktaları + range) + tick'ler */}
      <div className="timeline__track-wrap">
        <div className="timeline__era-strip" aria-hidden="true" />
        <div className="timeline__track-area">
          <EventMarker
            events={events}
            currentYear={currentYear}
            onSelect={setActiveEvent}
          />
          <input
            className="timeline__range"
            type="range"
            min={0}
            max={1}
            step={0.0001}
            value={t}
            aria-label={`Yıl ${currentYear}`}
            style={{ "--pct": t * 100 } as React.CSSProperties}
            onChange={(e) => {
              setPlaying(false);
              const next = parseFloat(e.target.value);
              setT(next);
              setEra(eraFromYear(yearFromT(next)));
            }}
          />
        </div>
        <div className="timeline__ticks" aria-hidden="true">
          {ERA_TICKS.map((year) => (
            <span
              key={year}
              className="timeline__tick"
              style={{ left: `${((year - YEAR_MIN) / YEAR_RANGE) * 100}%` }}
              data-active={currentYear >= year}
            >
              {year}
            </span>
          ))}
        </div>
        <div className="timeline__shortcut-hint" aria-hidden="true">
          SPACE oynat · ← / → yıl · SHIFT+← / → ×10
        </div>
      </div>

      {/* Sağ: müzik era radio pill'leri */}
      <div className="timeline__era" role="group" aria-label="Müzik dönemi">
        {ERA_ORDER.map((id) => (
          <button
            key={id}
            className="timeline__era-pill"
            data-active={era === id}
            onClick={() => setEra(id)}
            aria-pressed={era === id}
            title={`/public/cities/{şehir}/music/${id}.mp3`}
            style={{ "--era-color": ERA_ID_COLORS[id].hex } as React.CSSProperties}
          >
            {ERA_LABELS[id]}
          </button>
        ))}
      </div>
    </div>
  );
}
