import { useEffect, useRef } from "react";
import { useStore } from "@/store/useStore";

const FADE_DURATION = 1.5; // saniye — crossfade süresi
const VOLUME = 0.35;       // master volume (0–1)

/**
 * Era müzik motoru — Web Audio API native crossfade.
 * activeCity + era değişince yeni MP3 yükler, eski ses fade-out olur.
 * Kullanıcı etkileşimi olmadan AudioContext başlamaz (autoplay policy).
 * audioReady=true olduktan sonra devreye girer.
 */
export function useEraAudio() {
  const era = useStore((s) => s.era);
  const activeCity = useStore((s) => s.activeCity);
  const audioReady = useStore((s) => s.audioReady);
  const setAudioReady = useStore((s) => s.setAudioReady);

  const ctxRef = useRef<AudioContext | null>(null);
  const gainA = useRef<GainNode | null>(null);
  const gainB = useRef<GainNode | null>(null);
  const sourceA = useRef<AudioBufferSourceNode | null>(null);
  const sourceB = useRef<AudioBufferSourceNode | null>(null);
  const activeSlot = useRef<"a" | "b">("a");
  const loadedKey = useRef<string>(""); // "{city}/{era}"

  // AudioContext kullanıcı etkileşimi ile başlar
  useEffect(() => {
    const resume = () => {
      if (ctxRef.current) {
        ctxRef.current.resume().then(() => setAudioReady(true));
        return;
      }
      const ctx = new AudioContext();
      ctxRef.current = ctx;
      gainA.current = ctx.createGain();
      gainB.current = ctx.createGain();
      gainA.current.gain.value = 0;
      gainB.current.gain.value = 0;
      gainA.current.connect(ctx.destination);
      gainB.current.connect(ctx.destination);
      ctx.resume().then(() => setAudioReady(true));
    };

    window.addEventListener("click", resume, { once: true });
    window.addEventListener("keydown", resume, { once: true });
    return () => {
      window.removeEventListener("click", resume);
      window.removeEventListener("keydown", resume);
    };
  }, [setAudioReady]);

  // Era/city değişince crossfade
  useEffect(() => {
    if (!audioReady || !activeCity || !era) return;

    const ctx = ctxRef.current;
    if (!ctx) return;

    const key = `${activeCity}/${era}`;
    if (key === loadedKey.current) return; // aynı track, değiştirme
    loadedKey.current = key;

    const url = `/cities/${activeCity}/music/${era}.mp3`;

    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`404: ${url}`);
        return r.arrayBuffer();
      })
      .then((buf) => ctx.decodeAudioData(buf))
      .then((decoded) => {
        if (loadedKey.current !== key) return; // geç geldiyse iptal

        const next = activeSlot.current === "a" ? "b" : "a";
        const outGain = next === "b" ? gainA.current! : gainB.current!;
        const inGain  = next === "b" ? gainB.current! : gainA.current!;
        const outSrc  = next === "b" ? sourceA.current : sourceB.current;

        // Eski kaynak fade-out + stop
        const now = ctx.currentTime;
        outGain.gain.setValueAtTime(outGain.gain.value, now);
        outGain.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
        if (outSrc) {
          try { outSrc.stop(now + FADE_DURATION + 0.1); } catch (_) {}
        }

        // Yeni kaynak fade-in
        const src = ctx.createBufferSource();
        src.buffer = decoded;
        src.loop = true;
        src.connect(inGain);
        inGain.gain.setValueAtTime(0, now);
        inGain.gain.linearRampToValueAtTime(VOLUME, now + FADE_DURATION);
        src.start(now);

        // Slot güncelle
        if (next === "b") sourceB.current = src;
        else sourceA.current = src;
        activeSlot.current = next;
      })
      .catch(() => {
        // Placeholder — MP3 henüz yok, sessiz kal
      });
  }, [era, activeCity, audioReady]);

  // Şehir çıkınca durdur
  useEffect(() => {
    if (activeCity) return;
    const ctx = ctxRef.current;
    if (!ctx) return;
    const now = ctx.currentTime;
    gainA.current?.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
    gainB.current?.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
    loadedKey.current = "";
  }, [activeCity]);

  // Unmount: AudioContext kapat
  useEffect(() => {
    return () => {
      ctxRef.current?.close();
    };
  }, []);
}
