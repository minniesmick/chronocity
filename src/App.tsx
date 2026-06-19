import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import IntroScene from "@/components/IntroScene";
import GlobeSelector from "@/components/GlobeSelector";
import CityExperience from "@/components/CityExperience";
import "@/App.css";

export default function App() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<IntroScene />} />
        <Route path="/globe" element={<GlobeSelector />} />
        <Route path="/city/:id" element={<CityExperience />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}
