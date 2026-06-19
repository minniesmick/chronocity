import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import { CITIES } from "@/data/cities";
import type { CityId } from "@/types";
import MapCanvas from "@/components/MapCanvas";
import ArrowNarrowLeftIcon from "@/components/icons/arrow-narrow-left-icon";
import TimelineBar from "@/components/TimelineBar";
import DayNightToggle from "@/components/DayNightToggle";
import CityLoadingScreen from "@/components/CityLoadingScreen";
import EventPopup from "@/components/EventPopup";
import ReplayButton from "@/components/ReplayButton";
import FrequencyVisualizer from "@/components/FrequencyVisualizer";
import BuildingPopup from "@/components/BuildingPopup";
import { useEraAudio } from "@/hooks/useEraAudio";
import "@/components/sprint1.css";
import "@/components/sprint2.css";

export default function CityExperience() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isDayMode = useStore((s) => s.isDayMode);

  const city = id as CityId;
  const meta = CITIES[city];
  const setActiveCity = useStore((s) => s.setActiveCity);

  useEffect(() => {
    setActiveCity(city);
    return () => setActiveCity(null);
  }, [city, setActiveCity]);

  const [showLoading, setShowLoading] = useState(true);
  useEraAudio();

  if (!meta) {
    navigate("/globe");
    return null;
  }

  return (
    <div className="city-exp" data-day={isDayMode}>
      {/* Harita hep açık — loading screen üstüne overlay gelir */}
      <MapCanvas city={city} />

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
        <DayNightToggle />
      </motion.header>

      <TimelineBar />
      <FrequencyVisualizer />
      <BuildingPopup />
      <EventPopup />
      <ReplayButton />

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
