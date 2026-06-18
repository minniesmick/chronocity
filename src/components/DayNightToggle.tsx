import { useStore } from "@/store/useStore";

/**
 * Gece/Gündüz yapışık ikili buton. `isDayMode` store uniform'u → MapCanvas
 * lighting + bina paleti + arka plan değişir. Geçiş arka planda 800ms (CSS).
 */
export default function DayNightToggle() {
  const isDayMode = useStore((s) => s.isDayMode);
  const toggleDayMode = useStore((s) => s.toggleDayMode);

  return (
    <div className="daynight" role="group" aria-label="Gece / Gündüz">
      <button
        className="daynight__btn"
        data-on={isDayMode}
        aria-pressed={isDayMode}
        onClick={() => !isDayMode && toggleDayMode()}
      >
        ☀ Gündüz
      </button>
      <button
        className="daynight__btn"
        data-on={!isDayMode}
        aria-pressed={!isDayMode}
        onClick={() => isDayMode && toggleDayMode()}
      >
        ☾ Gece
      </button>
    </div>
  );
}
