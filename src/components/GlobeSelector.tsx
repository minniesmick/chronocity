import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import * as THREE from "three";
import { CITY_LIST } from "@/data/cities";
import type { CityMeta } from "@/types";

/** lat/lon → küre üzeri XYZ (lon=0,lat=0 → +Z ön) */
function latLonToVec3(lat: number, lon: number, r = 1): THREE.Vector3 {
  const latR = lat * (Math.PI / 180);
  const lonR = lon * (Math.PI / 180);
  return new THREE.Vector3(
    r * Math.cos(latR) * Math.sin(lonR),
    r * Math.sin(latR),
    r * Math.cos(latR) * Math.cos(lonR),
  );
}

export default function GlobeSelector() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const labelRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const [hoveredCity, setHoveredCity] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current!;
    const canvas = canvasRef.current!;
    const w = container.clientWidth;
    const h = container.clientHeight;

    // --- Renderer ---
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    // --- Scene & Camera ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    camera.position.set(0, 0.4, 5.2);
    camera.lookAt(0, 0, 0);

    // --- Işık ---
    scene.add(new THREE.AmbientLight(0x8899bb, 0.7));
    const sun = new THREE.DirectionalLight(0xf59e0b, 1.3);
    sun.position.set(4, 3, 5);
    scene.add(sun);
    const fill = new THREE.DirectionalLight(0x3355aa, 0.4);
    fill.position.set(-4, -1, -2);
    scene.add(fill);

    // --- Globe mesh ---
    const globeGeo = new THREE.SphereGeometry(2, 64, 64);
    const globeMat = new THREE.MeshPhongMaterial({
      color: 0x0d1b2a,
      emissive: 0x05101e,
      specular: 0x223355,
      shininess: 30,
    });
    const globe = new THREE.Mesh(globeGeo, globeMat);
    globe.scale.set(0.82, 0.82, 0.82); // mount animasyonu başlangıcı
    scene.add(globe);

    // Ince grid çizgileri (atmosfer hissi)
    const wireGeo = new THREE.SphereGeometry(2.005, 24, 16);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x1e3a5f,
      wireframe: true,
      opacity: 0.12,
      transparent: true,
    });
    globe.add(new THREE.Mesh(wireGeo, wireMat));

    // --- Şehir noktaları (globe'un çocuğu → onunla döner) ---
    const dotGeo = new THREE.SphereGeometry(0.045, 10, 10);
    const dots: { city: CityMeta; mesh: THREE.Mesh }[] = [];

    CITY_LIST.forEach((city) => {
      const [lon, lat] = city.center;
      const pos = latLonToVec3(lat, lon, 1.025);
      const mat = new THREE.MeshBasicMaterial({ color: city.color });
      const mesh = new THREE.Mesh(dotGeo, mat);
      mesh.position.copy(pos);
      mesh.userData.cityId = city.id;
      globe.add(mesh); // globe çocuğu → onunla döner
      dots.push({ city, mesh });
    });

    // --- Raycaster ---
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-99, -99);
    let hoveredId: string | null = null;

    const onMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    };

    let clickMoved = false;
    const onMouseDown = () => { clickMoved = false; };
    const onMouseMoveForClick = () => { clickMoved = true; };
    const onClick = () => {
      if (clickMoved) return;
      if (hoveredId) navigate(`/city/${hoveredId}`);
    };

    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mousemove", onMouseMoveForClick);
    canvas.addEventListener("mousedown", onMouseDown);
    canvas.addEventListener("click", onClick);

    // --- RAF animasyon döngüsü ---
    let rafId = 0;
    let mountFrame = 0; // scale-in sayacı
    const MOUNT_FRAMES = 80; // ~1.3s @60fps
    const worldPos = new THREE.Vector3();

    const animate = () => {
      rafId = requestAnimationFrame(animate);

      // Mount scale-in: ease-out-cubic 0.82 → 1.0
      if (mountFrame < MOUNT_FRAMES) {
        const p = mountFrame / MOUNT_FRAMES;
        const eased = 1 - Math.pow(1 - p, 3);
        const s = 0.82 + 0.18 * eased;
        globe.scale.set(s, s, s);
        mountFrame++;
      }

      // Yavaş oto-dönüş
      globe.rotation.y += 0.0008;

      // Raycasting — dot mesh'lere
      raycaster.setFromCamera(mouse, camera);
      const dotMeshes = dots.map((d) => d.mesh);
      const hits = raycaster.intersectObjects(dotMeshes);
      const newHovered = hits.length > 0 ? (hits[0].object.userData.cityId as string) : null;
      if (newHovered !== hoveredId) {
        hoveredId = newHovered;
        setHoveredCity(newHovered);
        canvas.style.cursor = newHovered ? "pointer" : "default";
      }

      // Dot ölçek: hover → büyür
      dots.forEach(({ city, mesh }) => {
        const target = hoveredId === city.id ? 1.7 : 1.0;
        mesh.scale.lerp(new THREE.Vector3(target, target, target), 0.15);
      });

      // Label konumu güncelle
      const cw = container.clientWidth;
      const ch = container.clientHeight;
      const camDir = camera.position.clone().normalize();

      dots.forEach(({ city, mesh }) => {
        const el = labelRefs.current[city.id];
        if (!el) return;
        mesh.getWorldPosition(worldPos);

        // Ön yüz kontrolü: kamera yönü ile nokta yönü aynı yarıkürede mi?
        const isFront = worldPos.clone().normalize().dot(camDir) > 0.05;
        if (!isFront) {
          el.style.opacity = "0";
          el.style.pointerEvents = "none";
          return;
        }

        const ndc = worldPos.clone().project(camera);
        const x = (ndc.x * 0.5 + 0.5) * cw;
        const y = (-ndc.y * 0.5 + 0.5) * ch;
        el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
        el.style.opacity = "1";
        el.style.pointerEvents = "auto";
      });

      renderer.render(scene, camera);
    };
    animate();

    // Resize
    const ro = new ResizeObserver(() => {
      const nw = container.clientWidth;
      const nh = container.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    });
    ro.observe(container);

    return () => {
      cancelAnimationFrame(rafId);
      canvas.removeEventListener("mousemove", onMouseMove);
      canvas.removeEventListener("mousemove", onMouseMoveForClick);
      canvas.removeEventListener("mousedown", onMouseDown);
      canvas.removeEventListener("click", onClick);
      ro.disconnect();
      renderer.dispose();
    };
  }, [navigate]);

  return (
    <motion.div
      className="globe-selector"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      ref={containerRef}
    >
      <canvas ref={canvasRef} className="globe-selector__canvas" />
      <div className="globe-selector__glow" aria-hidden="true" />

      {/* HTML label katmanı */}
      <div className="globe-labels" aria-hidden="true">
        {CITY_LIST.map((city) => (
          <div
            key={city.id}
            ref={(el) => { labelRefs.current[city.id] = el; }}
            className="globe-label"
            data-hovered={hoveredCity === city.id}
            onClick={() => navigate(`/city/${city.id}`)}
            style={{ "--city-color": city.color } as React.CSSProperties}
          >
            <span className="globe-label__flag">{city.flag}</span>
            <span className="globe-label__name">{city.name}</span>
          </div>
        ))}
      </div>

      {/* Alt bilgi */}
      <p className="globe-selector__hint">Bir şehre tıkla</p>
    </motion.div>
  );
}
