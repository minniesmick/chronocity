import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/store/useStore";

const ERAS = [
  { name: "Taş / Barok",   period: "< 1870",     rgb: [180, 150, 100] },
  { name: "Gründerzeit",   period: "1870–1918",   rgb: [190, 120,  80] },
  { name: "Art Deco",      period: "1918–1945",   rgb: [200, 165,  60] },
  { name: "Brutalizm",     period: "1945–1970",   rgb: [140, 150, 160] },
  { name: "Prefab",        period: "1970–1990",   rgb: [175, 175, 155] },
  { name: "Cam & Çelik",  period: "1990–2010",   rgb: [130, 175, 150] },
  { name: "Modern",        period: "≥ 2010",      rgb: [100, 170, 215] },
] as const;

function rgbStr(rgb: readonly [number, number, number], mul = 1) {
  return `rgb(${Math.round(rgb[0]*mul)},${Math.round(rgb[1]*mul)},${Math.round(rgb[2]*mul)})`;
}

export default function EraLegend() {
  const [open, setOpen] = useState(false);
  const isDayMode = useStore((s) => s.isDayMode);
  const currentZoom = useStore((s) => s.currentZoom);
  const mul = isDayMode ? 1 : 0.55;

  return (
    <div className="era-legend">
      <button
        className="era-legend__toggle"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label="Era renk legend"
      >
        <span className="era-legend__zoom" aria-label={`Zoom ${currentZoom.toFixed(1)}`}>
          {currentZoom.toFixed(1)}<span className="era-legend__zoom-x">×</span>
        </span>
        <span className="era-legend__divider" aria-hidden="true" />
        <span className="era-legend__dot-row" aria-hidden="true">
          {ERAS.map((e) => (
            <span
              key={e.name}
              className="era-legend__micro-dot"
              style={{ background: rgbStr(e.rgb, mul) }}
            />
          ))}
        </span>
        <span className="era-legend__label">Dönemler</span>
        <span className="era-legend__chevron" data-open={open}>›</span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="era-legend__panel"
            initial={{ opacity: 0, y: 6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.97 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
          >
            {ERAS.map((era) => (
              <div key={era.name} className="era-legend__row">
                <span
                  className="era-legend__swatch"
                  style={{ background: rgbStr(era.rgb, mul) }}
                />
                <span className="era-legend__era-name">{era.name}</span>
                <span className="era-legend__period">{era.period}</span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
