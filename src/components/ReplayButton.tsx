import { useRef } from "react";
import { useStore } from "@/store/useStore";
import RefreshIcon from "@/components/icons/refresh-icon";
import type { AnimatedIconHandle } from "@/components/icons/types";

export default function ReplayButton() {
  const setT = useStore((s) => s.setT);
  const setPlaying = useStore((s) => s.setPlaying);
  const iconRef = useRef<AnimatedIconHandle>(null);

  return (
    <button
      className="replay-btn"
      onClick={() => {
        setT(0);
        setPlaying(true);
        iconRef.current?.startAnimation();
      }}
      aria-label="Başa sar ve oynat"
      title="Başa sar"
    >
      <RefreshIcon ref={iconRef} size={18} color="currentColor" />
    </button>
  );
}
