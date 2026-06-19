import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import * as THREE from "three";
import { CITY_LIST } from "@/data/cities";
import { useStore } from "@/store/useStore";
import DayNightToggle from "@/components/DayNightToggle";
import type { CityMeta } from "@/types";

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
  const labelRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const [hoveredCity, setHoveredCity] = useState<string | null>(null);

  // Three.js refs — ikinci useEffect'ten erişmek için
  const globeMatRef = useRef<THREE.MeshPhongMaterial | null>(null);
  const texCacheRef = useRef<{ night: THREE.Texture | null; day: THREE.Texture | null }>({ night: null, day: null });
  const ambientRef  = useRef<THREE.AmbientLight | null>(null);
  const sunRef      = useRef<THREE.DirectionalLight | null>(null);
  const atmMatRef   = useRef<THREE.MeshBasicMaterial | null>(null);
  const isDayRef    = useRef(isDayMode); // başlangıç değeri texture yükleme kararı için

  useEffect(() => { isDayRef.current = isDayMode; }, [isDayMode]);

  // --- Ana sahne ---
  useEffect(() => {
    const container = containerRef.current!;
    const canvas = canvasRef.current!;
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
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    camera.position.set(0, 0.4, 5.2);
    camera.lookAt(0, 0, 0);

    // Işıklar (refs ile güncellenir)
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

    // Globe mesh
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

    // Grid (atmosfer hissi)
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

    // Şehir noktaları — lüks dot (büyük + parlak)
    const dotGeo  = new THREE.SphereGeometry(0.06, 16, 16);
    const ringGeo = new THREE.SphereGeometry(0.10, 16, 16);
    const dots: { city: CityMeta; mesh: THREE.Mesh }[] = [];

    CITY_LIST.forEach((city) => {
      const [lon, lat] = city.center;
      const pos = latLonToVec3(lat, lon, GLOBE_R * 1.015);
      const mesh = new THREE.Mesh(dotGeo, new THREE.MeshBasicMaterial({ color: city.color }));
      mesh.position.copy(pos);
      // Halo ring — şehir rengi, yarı şeffaf
      mesh.add(new THREE.Mesh(
        ringGeo,
        new THREE.MeshBasicMaterial({ color: city.color, transparent: true, opacity: 0.3 }),
      ));
      mesh.userData.cityId = city.id;
      globe.add(mesh);
      dots.push({ city, mesh });
    });

    // Drag + Raycaster state
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-99, -99);
    let hoveredId: string | null = null;
    let dragging = false, lastX = 0, lastY = 0, moved = 0, autoPause = 0;
    const dotMeshes = dots.map((d) => d.mesh);

    canvas.style.cursor = "grab";

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
    const onDown = (e: PointerEvent) => { dragging = true; moved = 0; lastX = e.clientX; lastY = e.clientY; };
    const onUp   = () => {
      if (dragging && moved < 6 && hoveredId) navigate(`/city/${hoveredId}`);
      dragging = false;
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
      else globe.rotation.y += 0.0008;

      raycaster.setFromCamera(mouse, camera);
      const hits = dragging ? [] : raycaster.intersectObjects(dotMeshes);
      const newHovered = hits.length > 0
        ? (hits[0].object.parent?.userData.cityId as string ?? null) : null;
      if (newHovered !== hoveredId) {
        hoveredId = newHovered;
        setHoveredCity(newHovered);
        if (!dragging) canvas.style.cursor = newHovered ? "pointer" : "grab";
      }

      dots.forEach(({ city, mesh }) => {
        const t = hoveredId === city.id ? 1.7 : 1.0;
        mesh.scale.lerp(new THREE.Vector3(t, t, t), 0.15);
      });

      // Label card konumları
      const cw = container.clientWidth;
      const ch = container.clientHeight;
      const camDir = camera.position.clone().normalize();

      dots.forEach(({ city, mesh }) => {
        const el = labelRefs.current[city.id];
        if (!el) return;
        mesh.getWorldPosition(worldPos);

        const isFront = worldPos.clone().normalize().dot(camDir) > 0.05;
        if (!isFront) { el.style.opacity = "0"; el.style.pointerEvents = "none"; return; }

        const ndc = worldPos.clone().project(camera);
        const x = (ndc.x * 0.5 + 0.5) * cw;
        const y = (-ndc.y * 0.5 + 0.5) * ch;
        const hov = hoveredId === city.id;

        // Kartın alt kenarı doğrudan dot üstüne gelsin (translateY -100% -10px)
        el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -100%) translateY(-10px) scale(${hov ? 1.05 : 1})`;
        el.style.opacity = "1";
        el.style.pointerEvents = "auto";
        el.dataset.hovered = String(hov);
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
  }, [navigate]);

  // Gündüz/Gece toggle — texture + ışık swap
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

  return (
    <motion.div
      className="globe-selector"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      ref={containerRef}
    >
      <canvas ref={canvasRef} className="globe-selector__canvas" style={{ cursor: "grab" }} />
      <div className="globe-selector__glow" aria-hidden="true" />

      {/* Lüks şehir etiket kartları */}
      <div className="globe-labels" aria-hidden="true">
        {CITY_LIST.map((city) => (
          <div
            key={city.id}
            ref={(el) => { labelRefs.current[city.id] = el; }}
            className="globe-city-card"
            data-hovered={hoveredCity === city.id}
            onClick={() => navigate(`/city/${city.id}`)}
            style={{ "--city-color": city.color } as React.CSSProperties}
          >
            <span className={`fi fi-${city.countryCode} gcc__flag`} aria-label={city.country} />
            <div className="gcc__body">
              <div className="gcc__name">{city.name}</div>
              <div className="gcc__country">{city.country}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Sağ üst: gündüz/gece toggle */}
      <div className="globe-selector__controls">
        <DayNightToggle />
      </div>

      <p className="globe-selector__hint">Sürükle · Döndür · Bir şehre tıkla</p>
    </motion.div>
  );
}
