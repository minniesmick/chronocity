import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import { CITIES } from "@/data/cities";
import { FEATURES } from "@/config";
import { yearFromT, tFromYear, eraFromYear, YEAR_MIN, YEAR_MAX } from "@/lib/time";
import type { CityId } from "@/types";
import MapCanvas from "@/components/MapCanvas";
import ArrowNarrowLeftIcon from "@/components/icons/arrow-narrow-left-icon";
import LocateIcon from "@/components/icons/locate-icon";
import TimelineBar from "@/components/TimelineBar";
import DayNightToggle from "@/components/DayNightToggle";
import CityLoadingScreen from "@/components/CityLoadingScreen";
import EventPopup from "@/components/EventPopup";
import ReplayButton from "@/components/ReplayButton";
import FrequencyVisualizer from "@/components/FrequencyVisualizer";
import BuildingPopup from "@/components/BuildingPopup";
import EraLegend from "@/components/EraLegend";
import { useEraAudio } from "@/hooks/useEraAudio";
import "@/components/sprint1.css";
import "@/components/sprint2.css";

/**
 * URL ?year= senkronu — t'ye abone olur, null render eder:
 * re-render maliyeti CityExperience'a sıçramaz.
 */
function YearUrlSync() {
  const t = useStore((s) => s.t);
  const year = yearFromT(t);
  useEffect(() => {
    const id = setTimeout(() => {
      window.history.replaceState(null, "", `?year=${year}`);
    }, 300);
    return () => clearTimeout(id);
  }, [year]);
  return null;
}

export default function CityExperience() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isDayMode = useStore((s) => s.isDayMode);
  const triggerCameraReset = useStore((s) => s.triggerCameraReset);

  const city = id as CityId;
  const meta = CITIES[city];
  const setActiveCity = useStore((s) => s.setActiveCity);

  useEffect(() => {
    setActiveCity(city);
    return () => setActiveCity(null);
  }, [city, setActiveCity]);

  // Deep-link: /city/:id?year=1931 → timeline o yıla açılır
  useEffect(() => {
    const p = new URLSearchParams(window.location.search).get("year");
    if (!p) return;
    const y = parseInt(p, 10);
    if (Number.isNaN(y)) return;
    const clamped = Math.max(YEAR_MIN, Math.min(YEAR_MAX, y));
    useStore.getState().setT(tFromYear(clamped));
    useStore.getState().setEra(eraFromYear(clamped));
  }, []);

  // meta yoksa globe'a dön — render sırasında navigate React anti-pattern'i
  useEffect(() => {
    if (!meta) navigate("/globe", { replace: true });
  }, [meta, navigate]);

  const [showLoading, setShowLoading] = useState(true);
  const [showShortcuts, setShowShortcuts] = useState(() => !localStorage.getItem('cc-shortcuts'));
  useEraAudio();

  useEffect(() => {
    if (!showShortcuts) return;
    const t = setTimeout(() => {
      setShowShortcuts(false);
      localStorage.setItem('cc-shortcuts', '1');
    }, 4500);
    return () => clearTimeout(t);
  }, [showShortcuts]);

  if (!meta) return null;

  return (
    <div className="city-exp" data-day={isDayMode}>
      {/* Harita hep açık — loading screen üstüne overlay gelir */}
      <MapCanvas city={city} />
      <YearUrlSync />

      <motion.header
        className="city-exp__top"
        initial={{ opacity: 0, y: -18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
      >
        <button
          className="city-exp__back"
          onClick={() => navigate("/globe")}
          aria-label="Globe'a dön"
        >
          <ArrowNarrowLeftIcon size={16} color="currentColor" /> geri
        </button>
        <span
          className="city-exp__name"
          style={{ "--c": meta.color } as React.CSSProperties}
        >
          <span className={`fi fi-${meta.countryCode} city-exp__flag`} aria-label={meta.country} />
          <span className="city-exp__dot" />
          {meta.name}
        </span>
        <span className="city-exp__spacer" />
        <button
          className="city-exp__recenter"
          onClick={triggerCameraReset}
          aria-label="Kamerayı sıfırla"
          title="Kamerayı sıfırla"
        >
          <LocateIcon size={15} color="currentColor" />
        </button>
        <DayNightToggle />
      </motion.header>

      {FEATURES.music && <FrequencyVisualizer />}
      <BuildingPopup />
      <EventPopup />

      <motion.div
        className="bottom-hud"
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.42, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      >
        <EraLegend />
        <TimelineBar />
        <ReplayButton />
      </motion.div>

      {/* Klavye kısayol overlay — ilk ziyarette 4.5sn */}
      <AnimatePresence>
        {showShortcuts && (
          <motion.div
            className="shortcut-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            onClick={() => { setShowShortcuts(false); localStorage.setItem('cc-shortcuts', '1'); }}
            aria-label="Klavye kısayolları"
          >
            <div className="shortcut-overlay__card">
              <div className="shortcut-overlay__row"><kbd>SPACE</kbd><span>Oynat / Durdur</span></div>
              <div className="shortcut-overlay__row"><kbd>Sol</kbd><kbd>Sag</kbd><span>Yıl değiştir</span></div>
              <div className="shortcut-overlay__row"><kbd>SHIFT</kbd><span>×10 hız</span></div>
              <div className="shortcut-overlay__row"><kbd>ESC</kbd><span>Bina bilgisi kapat</span></div>
              <p className="shortcut-overlay__dismiss">Herhangi bir yere tıkla</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading screen overlay — AnimatePresence ile smooth exit */}
      <AnimatePresence>
        {showLoading && (
          <CityLoadingScreen
            key={city}
            city={meta}
            onReady={() => setShowLoading(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
