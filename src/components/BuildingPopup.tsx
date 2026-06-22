import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import { eraByYear } from "@/lib/eraColors";

const POPUP_W = 260;
const POPUP_H = 170;

export default function BuildingPopup() {
  const ab = useStore((s) => s.activeBuilding);
  const setActiveBuilding = useStore((s) => s.setActiveBuilding);
  const closeRef = useRef<HTMLButtonElement>(null);

  // Escape ile kapat
  useEffect(() => {
    if (!ab) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setActiveBuilding(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [ab, setActiveBuilding]);

  return (
    <AnimatePresence>
      {ab && (() => {
        const p = ab.properties;
        const hasYear = p.construction_year != null;
        const era = eraByYear(hasYear ? p.construction_year! : null);
        // Cap at 500m (tallest buildings ~500m range, not 280)
        const heightPct = Math.min(100, Math.round((p.height / 500) * 100));

        const margin = 16;
        let px = ab.x + 14;
        let py = ab.y - POPUP_H - 14;
        if (px + POPUP_W > window.innerWidth - margin) px = ab.x - POPUP_W - 14;
        if (py < margin) py = ab.y + 14;

        return (
          <motion.div
            key={`${ab.x}-${ab.y}`}
            className="bpop"
            style={{
              left: px,
              top: py,
              "--bpop-accent": era.hex,
            } as React.CSSProperties}
            initial={{ opacity: 0, scale: 0.94, y: 6 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 6 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <button
              ref={closeRef}
              className="bpop__close"
              onClick={() => setActiveBuilding(null)}
              aria-label="Kapat"
            >
              ✕
            </button>

            <div className="bpop__name">{p.name ?? "Yapı"}</div>

            <div className="bpop__divider" />

            <div className="bpop__height-num">
              {Math.round(p.height)}
              <span className="bpop__unit"> m</span>
            </div>

            <div className="bpop__bar-track">
              <motion.div
                className="bpop__bar-fill"
                initial={{ width: 0 }}
                animate={{ width: `${heightPct}%` }}
                transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1], delay: 0.08 }}
              />
            </div>

            <div className="bpop__meta">
              {hasYear ? (
                <>
                  <span className="bpop__year">{p.construction_year}</span>
                  <span className="bpop__sep">◆</span>
                  <span className="bpop__era">{era.label}</span>
                </>
              ) : (
                <span className="bpop__year bpop__year--unknown">Yapım yılı bilinmiyor</span>
              )}
            </div>
          </motion.div>
        );
      })()}
    </AnimatePresence>
  );
}
