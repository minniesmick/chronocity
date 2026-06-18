import { useStore } from "@/store/useStore";
import { yearFromT, YEAR_MIN, YEAR_MAX } from "@/lib/time";

/**
 * GEÇİCİ geliştirme scrubber'ı. Gerçek TimelineBar = SPRINT 3.
 * `t`'yi sürerek bina morph'unu (yıla göre yükselme) görmek için.
 */
export default function DevTimeScrubber() {
  const t = useStore((s) => s.t);
  const setT = useStore((s) => s.setT);

  return (
    <div className="scrubber">
      <span className="scrubber__year">{yearFromT(t)}</span>
      <input
        className="scrubber__range"
        type="range"
        min={0}
        max={1}
        step={0.001}
        value={t}
        aria-label={`Yıl ${yearFromT(t)}`}
        onChange={(e) => setT(parseFloat(e.target.value))}
      />
      <span className="scrubber__bounds">
        {YEAR_MIN} – {YEAR_MAX}
      </span>
    </div>
  );
}
