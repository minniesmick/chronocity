import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import * as THREE from "three";
import { CITY_LIST, CITIES } from "@/data/cities";
import { useStore } from "@/store/useStore";
import DayNightToggle from "@/components/DayNightToggle";
import GlobeIcon from "@/components/icons/globe-icon";
import PlayerIcon from "@/components/icons/player-icon";
import type { AnimatedIconHandle } from "@/components/icons/types";
import type { CityMeta } from "@/types";

function hexToGlowRgba(hex: string, alpha = 0.14): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function latLonToVec3(lat: number, lon: number, r = 1): THREE.Vector3 {
  const phi = (lon + 180) * (Math.PI / 180);
  const theta = (90 - lat) * (Math.PI / 180);
  return new THREE.Vector3(
    -r * Math.cos(phi) * Math.sin(theta),
    r * Math.cos(theta),
    r * Math.sin(phi) * Math.sin(theta),
  );
}

export default function GlobeSelector() {
  const navigate = useNavigate();
  const isDayMode = useStore((s) => s.isDayMode);
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredCity, setHoveredCity] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);
  const [isRotating, setIsRotating] = useState(true);
  const [showHint, setShowHint] = useState(() => !localStorage.getItem('cc-hint'));

  // DOM refs — updated directly in RAF (no React re-renders)
  const dotRefs  = useRef<Record<string, HTMLDivElement | null>>({});
  const cardRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const lineRefs = useRef<Record<string, SVGLineElement | null>>({});
  const svgRef   = useRef<SVGSVGElement>(null);

  // Refs for RAF closure access without stale state
  const selectedRef      = useRef<string | null>(null);
  const hoveredRef       = useRef<string | null>(null);
  const pausedByUserRef  = useRef(false);
  const autoPausedRef    = useRef(false);
  const globeIconRef     = useRef<AnimatedIconHandle>(null);

  // Three.js refs
  const globeMatRef = useRef<THREE.MeshPhongMaterial | null>(null);
  const texCacheRef = useRef<{ night: THREE.Texture | null; day: THREE.Texture | null }>({ night: null, day: null });
  const ambientRef  = useRef<THREE.AmbientLight | null>(null);
  const sunRef      = useRef<THREE.DirectionalLight | null>(null);
  const atmMatRef   = useRef<THREE.MeshBasicMaterial | null>(null);
  const isDayRef    = useRef(isDayMode);

  useEffect(() => { isDayRef.current = isDayMode; }, [isDayMode]);
  useEffect(() => {
    if (!showHint) return;
    const t = setTimeout(() => {
      setShowHint(false);
      localStorage.setItem('cc-hint', '1');
    }, 4000);
    return () => clearTimeout(t);
  }, [showHint]);
  useEffect(() => { globeIconRef.current?.startAnimation(); }, []);
  useEffect(() => { selectedRef.current = selectedCity; }, [selectedCity]);
  useEffect(() => { hoveredRef.current = hoveredCity; }, [hoveredCity]);

  const pauseGlobe = useCallback(() => {
    if (!pausedByUserRef.current) {
      pausedByUserRef.current = true;
      autoPausedRef.current = true;
      setIsRotating(false);
      globeIconRef.current?.stopAnimation();
    }
  }, []);

  const resumeGlobe = useCallback(() => {
    if (autoPausedRef.current) {
      pausedByUserRef.current = false;
      autoPausedRef.current = false;
      setIsRotating(true);
      globeIconRef.current?.startAnimation();
    }
  }, []);

  const toggleRotation = useCallback(() => {
    // Manual toggle overrides auto-pause
    autoPausedRef.current = false;
    const willPause = !pausedByUserRef.current;
    pausedByUserRef.current = willPause;
    setIsRotating(!willPause);
    if (willPause) globeIconRef.current?.stopAnimation();
    else globeIconRef.current?.startAnimation();
  }, []);

  const closeSelected = useCallback(() => {
    setSelectedCity(null);
    resumeGlobe();
  }, [resumeGlobe]);

  // --- Ana sahne ---
  useEffect(() => {
    const container = containerRef.current!;
    const canvas    = canvasRef.current!;
    const w = container.clientWidth;
    const h = container.clientHeight;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    if ("outputColorSpace" in renderer) {
      (renderer as any).outputColorSpace = THREE.SRGBColorSpace;
    }

    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(36, w / h, 0.1, 100);
    camera.position.set(0, 0.15, 6.4); // zoomed out — cards fit
    camera.lookAt(0, 0, 0);

    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    ambientRef.current = ambient;
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xf59e0b, 0.45);
    sun.position.set(5, 2, 4);
    sunRef.current = sun;
    scene.add(sun);

    const fill = new THREE.DirectionalLight(0x2a4a7a, 0.35);
    fill.position.set(-4, -1, -2);
    scene.add(fill);

    const GLOBE_R = 2;
    const globeMat = new THREE.MeshPhongMaterial({
      color: 0x5e6f86,
      emissive: 0x05090f,
      specular: 0x1a2636,
      shininess: 10,
    });
    globeMatRef.current = globeMat;
    const globe = new THREE.Mesh(new THREE.SphereGeometry(GLOBE_R, 64, 64), globeMat);
    globe.scale.set(0.82, 0.82, 0.82);
    scene.add(globe);

    // Atmosfer rim
    const atmMat = new THREE.MeshBasicMaterial({ color: 0x2b6fb0, transparent: true, opacity: 0.10, side: THREE.BackSide });
    atmMatRef.current = atmMat;
    globe.add(new THREE.Mesh(new THREE.SphereGeometry(GLOBE_R * 1.06, 64, 64), atmMat));

    // Grid
    globe.add(new THREE.Mesh(
      new THREE.SphereGeometry(GLOBE_R * 1.003, 24, 16),
      new THREE.MeshBasicMaterial({ color: 0x1e3a5f, wireframe: true, transparent: true, opacity: 0.10 }),
    ));

    // Texture yükle
    const loader = new THREE.TextureLoader();
    const applyTex = (tex: THREE.Texture) => {
      try { tex.anisotropy = renderer.capabilities.getMaxAnisotropy(); } catch (_) {}
      if ("colorSpace" in tex) (tex as any).colorSpace = THREE.SRGBColorSpace;
      globeMat.map = tex;
      globeMat.color.set(0xffffff);
      globeMat.needsUpdate = true;
    };
    loader.load("/textures/earth-night.jpg", (tex) => {
      texCacheRef.current.night = tex;
      if (!isDayRef.current) applyTex(tex);
      else globeMat.color.setHex(0x0d1b2a);
    }, undefined, () => { globeMat.color.setHex(0x0d1b2a); });
    loader.load("/textures/earth-day.jpg", (tex) => {
      texCacheRef.current.day = tex;
      if (isDayRef.current) applyTex(tex);
    });

    // Şehir noktaları — nearly invisible, sadece raycasting için
    const dotGeo = new THREE.SphereGeometry(0.22, 16, 16);
    const dots: { city: CityMeta; mesh: THREE.Mesh }[] = [];

    CITY_LIST.forEach((city) => {
      const [lon, lat] = city.center;
      const pos = latLonToVec3(lat, lon, GLOBE_R * 1.015);
      const mesh = new THREE.Mesh(
        dotGeo,
        new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.001 }),
      );
      mesh.position.copy(pos);
      mesh.userData.cityId = city.id;
      globe.add(mesh);
      dots.push({ city, mesh });
    });

    // Drag & raycaster
    const raycaster = new THREE.Raycaster();
    const mouse   = new THREE.Vector2(-99, -99);
    const dotMeshes = dots.map((d) => d.mesh);
    let hoveredId: string | null = null;
    let clickedId: string | null = null;
    let dragging = false, lastX = 0, lastY = 0, moved = 0, autoPause = 0;

    const onMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      if (dragging) {
        const dx = e.clientX - lastX, dy = e.clientY - lastY;
        moved += Math.abs(dx) + Math.abs(dy);
        globe.rotation.y += dx * 0.005;
        globe.rotation.x = Math.max(-0.6, Math.min(0.6, globe.rotation.x + dy * 0.005));
        lastX = e.clientX; lastY = e.clientY;
        autoPause = 90;
        canvas.style.cursor = "grabbing";
      }
    };
    const onDown = (e: PointerEvent) => {
      dragging = true; moved = 0; lastX = e.clientX; lastY = e.clientY;
      clickedId = hoveredId; // capture before RAF clears it during drag
    };
    const onUp = () => {
      if (dragging && moved < 6) {
        const target = clickedId;
        if (target) {
          const cur = selectedRef.current;
          if (cur === target) {
            setSelectedCity(null);
            resumeGlobe();
          } else {
            setSelectedCity(target);
            pauseGlobe();
          }
        } else if (selectedRef.current) {
          setSelectedCity(null);
          resumeGlobe();
        }
      }
      dragging = false;
      clickedId = null;
      canvas.style.cursor = hoveredId ? "pointer" : "grab";
    };

    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerdown", onDown);
    window.addEventListener("pointerup", onUp);

    let rafId = 0, mountFrame = 0;
    const MOUNT_FRAMES = 80;
    const worldPos = new THREE.Vector3();

    const animate = () => {
      rafId = requestAnimationFrame(animate);

      if (mountFrame < MOUNT_FRAMES) {
        const eased = 1 - Math.pow(1 - mountFrame / MOUNT_FRAMES, 3);
        globe.scale.setScalar(0.82 + 0.18 * eased);
        mountFrame++;
      }

      if (autoPause > 0) autoPause--;
      else if (!pausedByUserRef.current) globe.rotation.y += 0.0008;

      // Raycasting — hover detection
      raycaster.setFromCamera(mouse, camera);
      const hits = dragging ? [] : raycaster.intersectObjects(dotMeshes);
      const newHovered = hits.length > 0
        ? (hits[0].object.userData.cityId as string ?? null) : null;
      if (newHovered !== hoveredId) {
        hoveredId = newHovered;
        setHoveredCity(newHovered);
        if (!dragging) canvas.style.cursor = newHovered ? "pointer" : "grab";
      }

      // Project cities → 2D, update HTML dots / SVG lines / cards
      const cw = container.clientWidth;
      const ch = container.clientHeight;
      const cx = cw / 2;
      const cy = ch / 2;
      const camDir = camera.position.clone().normalize();

      dots.forEach(({ city, mesh }) => {
        const dotEl  = dotRefs.current[city.id];
        const line   = lineRefs.current[city.id];
        const card   = cardRefs.current[city.id];

        mesh.getWorldPosition(worldPos);
        const isFront = worldPos.clone().normalize().dot(camDir) > 0.08;

        const isHov = hoveredId === city.id;
        const isSel = selectedRef.current === city.id;

        if (!isFront) {
          if (dotEl)  { dotEl.style.opacity = "0"; }
          if (line)   { line.style.opacity = "0"; }
          if (card)   { card.classList.remove('city-card--visible'); }
          return;
        }

        const ndc = worldPos.clone().project(camera);
        const x = (ndc.x * 0.5 + 0.5) * cw;
        const y = (-ndc.y * 0.5 + 0.5) * ch;

        // Outward direction (from globe center → city point)
        const dx = x - cx, dy = y - cy;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const nx = dx / dist, ny = dy / dist;
        const lineLen = isSel ? 110 : isHov ? 95 : 80;
        let lx2 = x + nx * lineLen;
        let ly2 = y + ny * lineLen;

        // Dot
        if (dotEl) {
          dotEl.style.left = `${x}px`;
          dotEl.style.top  = `${y}px`;
          dotEl.style.opacity = "1";
          dotEl.dataset.hovered  = String(isHov);
          dotEl.dataset.selected = String(isSel);
          (dotEl.style as any)["--city-color"] = city.color;
        }

        // Card viewport clamp — prevent cards from leaving screen
        const CARD_W = 220, CARD_H_MIN = 56;
        const isRight = x > cx + 30;
        const isLeft  = x < cx - 30;
        const m = 14; // margin from viewport edge

        if (isRight)  lx2 = Math.min(lx2, cw - CARD_W - m - 14);
        else if (isLeft) lx2 = Math.max(lx2, CARD_W + m + 14);
        // Vertical clamp: card centered at ly2, so clamp by half height
        ly2 = Math.max(CARD_H_MIN / 2 + 60 + m, Math.min(ly2, ch - CARD_H_MIN / 2 - m - 64));

        // SVG line
        if (line) {
          line.setAttribute("x1", String(x));
          line.setAttribute("y1", String(y));
          line.setAttribute("x2", String(lx2));
          line.setAttribute("y2", String(ly2));
          line.setAttribute("stroke", city.color);
          line.dataset.visible = String(isHov || isSel);
        }

        // Card
        if (card) {
          let tx = "0px", ty = "-50%";
          if (isRight)     tx = "14px";
          else if (isLeft) tx = "calc(-100% - 14px)";
          else             tx = "-50%";

          card.style.left      = `${lx2}px`;
          card.style.top       = `${ly2}px`;
          card.style.transform = `translate(${tx}, ${ty})`;
          card.classList.toggle('city-card--visible', isHov || isSel);
          card.dataset.selected = String(isSel);
        }
      });

      renderer.render(scene, camera);
    };
    animate();

    const ro = new ResizeObserver(() => {
      const nw = container.clientWidth, nh = container.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    });
    ro.observe(container);

    return () => {
      cancelAnimationFrame(rafId);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerdown", onDown);
      window.removeEventListener("pointerup", onUp);
      ro.disconnect();
      renderer.dispose();
    };
  }, [navigate, pauseGlobe, resumeGlobe]);

  // Gündüz/Gece texture + ışık swap
  useEffect(() => {
    const mat = globeMatRef.current;
    if (!mat) return;
    const tex = isDayMode ? texCacheRef.current.day : texCacheRef.current.night;
    if (tex) { mat.map = tex; mat.color.set(0xffffff); mat.needsUpdate = true; }
    if (ambientRef.current) ambientRef.current.intensity = isDayMode ? 1.0 : 0.6;
    if (sunRef.current) {
      sunRef.current.intensity = isDayMode ? 0.9 : 0.45;
      sunRef.current.color.setHex(isDayMode ? 0xfff5e0 : 0xf59e0b);
    }
    if (atmMatRef.current) {
      atmMatRef.current.color.setHex(isDayMode ? 0x5ba8d4 : 0x2b6fb0);
      atmMatRef.current.opacity = isDayMode ? 0.06 : 0.10;
    }
  }, [isDayMode]);

  const glowColor = hoveredCity && CITIES[hoveredCity as keyof typeof CITIES]
    ? hexToGlowRgba(CITIES[hoveredCity as keyof typeof CITIES].color, 0.14)
    : selectedCity && CITIES[selectedCity as keyof typeof CITIES]
    ? hexToGlowRgba(CITIES[selectedCity as keyof typeof CITIES].color, 0.10)
    : "rgba(245,158,11,0.07)";

  return (
    <motion.div
      className="globe-selector"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      ref={containerRef}
      onClick={closeSelected}
    >
      <canvas ref={canvasRef} className="globe-selector__canvas" style={{ cursor: "grab" }} onClick={(e) => e.stopPropagation()} />

      {/* Ambient glow — dinamik renk */}
      <div
        className="globe-selector__glow"
        aria-hidden="true"
        style={{ "--glow-color": glowColor } as React.CSSProperties}
      />

      {/* SVG connector lines */}
      <svg ref={svgRef} className="globe-svg-layer" aria-hidden="true">
        {CITY_LIST.map((city) => (
          <line
            key={city.id}
            ref={(el) => { lineRefs.current[city.id] = el; }}
            strokeWidth="1"
            strokeLinecap="round"
            strokeDasharray="5 4"
          />
        ))}
      </svg>

      {/* 2D city dots */}
      {CITY_LIST.map((city) => (
        <div
          key={city.id}
          ref={(el) => { dotRefs.current[city.id] = el; }}
          className="city-dot"
          style={{ "--city-color": city.color } as React.CSSProperties}
          aria-hidden="true"
        />
      ))}

      {/* City info cards */}
      {CITY_LIST.map((city) => {
        const stats = city.stats;
        const isSel = selectedCity === city.id;
        return (
          <div
            key={city.id}
            ref={(el) => { cardRefs.current[city.id] = el; }}
            className="city-card"
            style={{ "--city-color": city.color } as React.CSSProperties}
            onClick={(e) => {
              e.stopPropagation();
              if (isSel) { closeSelected(); } else { setSelectedCity(city.id); pauseGlobe(); }
            }}
          >
            <div className="city-card__header">
              <span className={`fi fi-${city.countryCode} city-card__flag`} aria-label={city.country} />
              <div className="city-card__titles">
                <div className="city-card__name">{city.name}</div>
                <div className="city-card__country">{city.country}</div>
              </div>
              {isSel && (
                <button
                  className="city-card__close"
                  onClick={(e) => { e.stopPropagation(); closeSelected(); }}
                  aria-label="Kapat"
                >✕</button>
              )}
            </div>

            <div className="city-card__detail" data-open={isSel}>
              {stats && (
                <div className="city-card__stats">
                  <div className="city-card__stat">
                    <span>NÜFUS</span>
                    <span>{stats.population}</span>
                  </div>
                  <div className="city-card__stat">
                    <span>KURULUŞ</span>
                    <span>{stats.founded}</span>
                  </div>
                </div>
              )}
              {stats?.milestones && (
                <div className="city-card__milestones">
                  {stats.milestones.slice(0, 2).map((m) => (
                    <div key={m} className="city-card__milestone">{m}</div>
                  ))}
                </div>
              )}
              <button
                className="city-card__fly"
                onClick={(e) => { e.stopPropagation(); navigate(`/city/${city.id}`); }}
                disabled={!city.hasBuildingData}
                title={!city.hasBuildingData ? "Bina verisi henüz yok" : undefined}
              >
                FLY TO {city.name.toUpperCase()} ›
              </button>
            </div>
          </div>
        );
      })}

      {/* TOP BAR */}
      <header className="globe-top-bar" onClick={(e) => e.stopPropagation()}>
        <div className="globe-wordmark" aria-label="ChronoCity">
          <span className="globe-wordmark__chrono">CHRONO</span>
          <span className="globe-wordmark__city">CITY</span>
        </div>
        <div className="globe-top-bar__spacer" />
        <DayNightToggle />
      </header>

      {/* BOTTOM BAR */}
      <footer className="globe-bottom-bar" onClick={(e) => e.stopPropagation()}>
        <button
          className="globe-spin-btn"
          onClick={toggleRotation}
          aria-label={isRotating ? "Küreyi durdur" : "Küreyi döndür"}
          data-rotating={isRotating}
        >
          <GlobeIcon ref={globeIconRef} size={14} color="currentColor" />
          <span>{isRotating ? "Durdur" : "Döndür"}</span>
          {!isRotating && <PlayerIcon size={10} color="currentColor" />}
        </button>

        <div className="globe-city-counter" aria-label="11 şehir, 170 bin üzeri bina">
          <span>11 şehir</span>
          <span className="globe-city-counter__sep" aria-hidden="true">·</span>
          <span>170K+ bina</span>
        </div>

        <div className="globe-bottom-bar__spacer" />

        {showHint && (
          <p className="globe-selector__hint" aria-hidden="true">
            Sürükle · Döndür · Bir şehre tıkla
          </p>
        )}
      </footer>
    </motion.div>
  );
}
