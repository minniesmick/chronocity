import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { CityMeta } from "@/types";

interface Props {
  city: CityMeta;
  onReady: () => void;
}

/**
 * Sprint 2 — Şehir geçiş ekranı.
 * TODO: <video className="city-loading__bg" loop muted autoPlay playsInline
 *         src={`/cities/${city.id}/intro.mp4`} />
 *       Şimdilik gradient placeholder.
 */
export default function CityLoadingScreen({ city, onReady }: Props) {
  const [milestoneIdx, setMilestoneIdx] = useState(0);
  const [progress, setProgress] = useState(0);

  // Milestones typewriter: her 600ms bir sonraki
  useEffect(() => {
    if (!city.stats?.milestones) return;
    const iv = setInterval(() => {
      setMilestoneIdx((i) => {
        if (i >= (city.stats?.milestones.length ?? 0) - 1) {
          clearInterval(iv);
          return i;
        }
        return i + 1;
      });
    }, 600);
    return () => clearInterval(iv);
  }, [city.id]);

  // Progress bar: 1.8s dolunca onReady — setTimeout (RAF arka planda throttle olur)
  useEffect(() => {
    setProgress(0);
    setMilestoneIdx(0);
    const DURATION = 1800;
    const STEPS = 36; // ~50ms aralık
    let step = 0;
    const iv = setInterval(() => {
      step++;
      setProgress(step / STEPS);
      if (step >= STEPS) {
        clearInterval(iv);
        onReady();
      }
    }, DURATION / STEPS);
    return () => clearInterval(iv);
  }, [city.id]);

  return (
    <motion.div
      className="city-loading"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* TODO: city video bg
      <video className="city-loading__bg" loop muted autoPlay playsInline
        src={`/cities/${city.id}/intro.mp4`} />
      */}
      <div className="city-loading__overlay" />

      <div className="city-loading__content">
        <span className="city-loading__flag">{city.flag}</span>
        <h2 className="city-loading__name" style={{ color: city.color }}>
          {city.name}
        </h2>
        <p className="city-loading__country">{city.country}</p>

        {city.stats && (
          <div className="city-loading__stats">
            <p className="city-loading__stat">
              <span className="city-loading__stat-label">Nüfus</span>
              <span>{city.stats.population}</span>
            </p>
            <p className="city-loading__stat">
              <span className="city-loading__stat-label">Kuruluş</span>
              <span>{city.stats.founded}</span>
            </p>
          </div>
        )}

        {city.stats?.milestones && (
          <ul className="city-loading__milestones">
            {city.stats.milestones.slice(0, milestoneIdx + 1).map((m) => (
              <motion.li
                key={m}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.35 }}
                className="city-loading__milestone"
              >
                {m}
              </motion.li>
            ))}
          </ul>
        )}
      </div>

      {/* Progress bar */}
      <div className="city-loading__bar-track">
        <div
          className="city-loading__bar-fill"
          style={{ width: `${progress * 100}%` }}
        />
      </div>
    </motion.div>
  );
}
