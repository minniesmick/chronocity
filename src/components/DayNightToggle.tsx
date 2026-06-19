import { useStore } from "@/store/useStore";
import BrightnessDownIcon from "@/components/icons/brightness-down-icon";
import MoonIcon from "@/components/icons/moon-icon";

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
        <BrightnessDownIcon size={14} color="currentColor" />
        Gündüz
      </button>
      <button
        className="daynight__btn"
        data-on={!isDayMode}
        aria-pressed={!isDayMode}
        onClick={() => isDayMode && toggleDayMode()}
      >
        <MoonIcon size={14} color="currentColor" />
        Gece
      </button>
    </div>
  );
}
