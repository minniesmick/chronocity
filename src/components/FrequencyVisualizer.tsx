import { useEffect, useRef } from "react";
import { useStore } from "@/store/useStore";
import { analyser } from "@/lib/audioContext";

const BAR_COUNT = 32;     // 32 frekans çubuğu
const BAR_W = 3;          // px
const BAR_GAP = 2;        // px
const MAX_H = 48;         // px — max bar yüksekliği
const CANVAS_W = BAR_COUNT * (BAR_W + BAR_GAP) - BAR_GAP;
const CANVAS_H = MAX_H;
const AMBER = "#f59e0b";

export default function FrequencyVisualizer() {
  const audioReady = useStore((s) => s.audioReady);
  const activeCity = useStore((s) => s.activeCity);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    if (!audioReady || !activeCity) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx2d = canvas.getContext("2d");
    if (!ctx2d) return;

    const fftSize = analyser?.frequencyBinCount ?? BAR_COUNT;
    const dataArr = new Uint8Array(fftSize);

    const draw = () => {
      rafRef.current = requestAnimationFrame(draw);
      if (!analyser) return;

      analyser.getByteFrequencyData(dataArr);

      ctx2d.clearRect(0, 0, CANVAS_W, CANVAS_H);

      // Her bar için FFT verisi — ilk 32 bin (düşük-orta frekanslar, müzikal)
      const step = Math.floor(fftSize / BAR_COUNT);
      for (let i = 0; i < BAR_COUNT; i++) {
        const val = dataArr[i * step] / 255;
        const h = Math.max(2, val * MAX_H);
        const x = i * (BAR_W + BAR_GAP);
        const y = CANVAS_H - h;

        // Gradient: taban amber → üst şeffaf
        const grad = ctx2d.createLinearGradient(x, y, x, CANVAS_H);
        grad.addColorStop(0, `${AMBER}99`);  // üst: %60 opacity
        grad.addColorStop(1, `${AMBER}ff`);  // taban: tam amber

        ctx2d.fillStyle = grad;
        ctx2d.fillRect(x, y, BAR_W, h);
      }
    };

    draw();
    return () => cancelAnimationFrame(rafRef.current);
  }, [audioReady, activeCity]);

  // Müzik yokken gizle
  if (!audioReady || !activeCity) return null;

  return (
    <canvas
      ref={canvasRef}
      className="freq-viz"
      width={CANVAS_W}
      height={CANVAS_H}
      aria-hidden="true"
    />
  );
}
