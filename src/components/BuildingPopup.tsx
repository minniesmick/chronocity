import { useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import { eraByYear } from "@/lib/eraColors";

const POPUP_W = 260;
const POPUP_H = 170;

export default function BuildingPopup() {
  const ab = useStore((s) => s.activeBuilding);
  const setActiveBuilding = useStore((s) => s.setActiveBuilding);
  const closeRef = useRef<HTMLButtonElement>(null);

  return (
    <AnimatePresence>
      {ab && (() => {
        const p = ab.properties;
        const era = eraByYear(p.construction_year);
        const heightPct = Math.min(100, Math.round((p.height / 280) * 100));

        // Viewport clamp — popup yukarı-sola açılır, kenara dayandı mı kontrol et
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

            <div className="bpop__name">
              {p.name ?? "Yapı"}
            </div>

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
              <span className="bpop__year">
                {p.construction_year ?? "—"}
              </span>
              <span className="bpop__sep">◆</span>
              <span className="bpop__era">{era.label}</span>
            </div>
          </motion.div>
        );
      })()}
    </AnimatePresence>
  );
}
