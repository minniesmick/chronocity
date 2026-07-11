import { lazy, Suspense } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import IntroScene from "@/components/IntroScene";
import "@/App.css";

// Route-level code splitting: Three.js yalnız globe'da, deck.gl yalnız city'de
// yüklenir — intro ikisinin de parse bedelini ödemez.
const GlobeSelector = lazy(() => import("@/components/GlobeSelector"));
const CityExperience = lazy(() => import("@/components/CityExperience"));

export default function App() {
  const location = useLocation();
  return (
    <Suspense fallback={<div style={{ position: "fixed", inset: 0, background: "var(--color-bg)" }} />}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<IntroScene />} />
          <Route path="/globe" element={<GlobeSelector />} />
          <Route path="/city/:id" element={<CityExperience />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </Suspense>
  );
}
