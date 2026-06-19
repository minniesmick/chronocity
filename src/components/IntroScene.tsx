import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

/**
 * Sprint 2 — Giriş ekranı.
 * TODO: <video className="intro__bg" loop muted autoPlay playsInline src="/videos/intro.mp4" />
 *       Şimdilik gradient arka plan placeholder.
 */
export default function IntroScene() {
  const navigate = useNavigate();

  return (
    <motion.div
      className="intro"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* TODO: video arka plan
      <video className="intro__bg" loop muted autoPlay playsInline src="/videos/intro.mp4" />
      */}
      <div className="intro__gradient" />
      <div className="intro__scanlines" aria-hidden="true" />

      <div className="intro__content">
        <motion.p
          className="intro__eyebrow"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          TEKNO-SİNEMATİK · KENTSEL ZAMAN YOLCULUĞU
        </motion.p>

        <motion.h1
          className="intro__wordmark"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          Chrono<span className="intro__accent">City</span>
        </motion.h1>

        <motion.p
          className="intro__tagline"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9, duration: 0.6 }}
        >
          Şehirlerin dönüşümünü zaman içinde 3D gez,<br />
          her dönemin sesini duy.
        </motion.p>

        <motion.button
          className="intro__enter"
          onClick={() => navigate("/globe")}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.2, duration: 0.5 }}
          whileHover={{ scale: 1.06, transition: { duration: 0.2 } }}
          whileTap={{ scale: 0.96 }}
        >
          KEŞFET →
        </motion.button>
      </div>
    </motion.div>
  );
}
