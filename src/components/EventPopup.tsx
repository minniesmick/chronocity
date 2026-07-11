import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import type { EventType } from "@/types";

const TYPE_COLOR: Record<EventType, string> = {
  positive: "#22c55e",
  negative: "#ef4444",
  neutral: "#f59e0b",
};

const TYPE_LABEL: Record<EventType, string> = {
  positive: "Gelişme",
  negative: "Kırılma",
  neutral: "Dönüm Noktası",
};

export default function EventPopup() {
  const activeEvent = useStore((s) => s.activeEvent);
  const setActiveEvent = useStore((s) => s.setActiveEvent);
  const ref = useRef<HTMLDivElement>(null);
  const ev = activeEvent;
  const visible = !!ev;

  // ESC kapat
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setActiveEvent(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setActiveEvent]);

  // Dışarı tıkla kapat
  useEffect(() => {
    if (!visible) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setActiveEvent(null);
      }
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [visible, setActiveEvent]);

  const color = ev ? TYPE_COLOR[ev.type] : "#f59e0b";
  const year = ev ? parseInt(ev.date.slice(0, 4), 10) : null;
  // Events içeriği akademik İngilizce, slug'lar EN Wikipedia'dan
  const wikiUrl = ev?.wikiSlug
    ? `https://en.wikipedia.org/wiki/${ev.wikiSlug}`
    : null;

  return (
    <div className="event-popup-anchor">
      <motion.div
        ref={ref}
        className="event-popup"
        role={visible ? "dialog" : undefined}
        aria-label={ev?.title}
        aria-hidden={!visible}
        animate={{
          opacity: visible ? 1 : 0,
          y: visible ? 0 : 14,
          scale: visible ? 1 : 0.97,
        }}
        transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
        initial={{ opacity: 0, y: 14, scale: 0.97 }}
        style={{ "--ev-color": color } as React.CSSProperties}
      >
        {ev && (
          <>
            <div className="event-popup__header">
              <span className="event-popup__badge">{TYPE_LABEL[ev.type]}</span>
              <span className="event-popup__year">{year}</span>
              <button
                className="event-popup__close"
                onClick={() => setActiveEvent(null)}
                aria-label="Kapat"
              >
                ×
              </button>
            </div>

            <h3 className="event-popup__title">{ev.title}</h3>
            <p className="event-popup__desc">{ev.shortDesc}</p>

            {wikiUrl && (
              <a
                className="event-popup__more"
                href={wikiUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                Daha fazla →
              </a>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
}
