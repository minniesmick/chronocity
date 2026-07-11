import { useEffect, useRef } from "react";
import { FEATURES } from "@/config";
import { useStore } from "@/store/useStore";
import { getAudioContext, masterGain } from "@/lib/audioContext";

const FADE_DURATION = 1.5;
const VOLUME = 0.35;

export function useEraAudio() {
  const era = useStore((s) => s.era);
  const activeCity = useStore((s) => s.activeCity);
  const audioReady = useStore((s) => s.audioReady);
  const setAudioReady = useStore((s) => s.setAudioReady);

  const gainA = useRef<GainNode | null>(null);
  const gainB = useRef<GainNode | null>(null);
  const sourceA = useRef<AudioBufferSourceNode | null>(null);
  const sourceB = useRef<AudioBufferSourceNode | null>(null);
  const activeSlot = useRef<"a" | "b">("a");
  const loadedKey = useRef<string>("");

  // AudioContext lazy init — kullanıcı etkileşimi gerekir
  useEffect(() => {
    if (!FEATURES.music) return;
    const resume = () => {
      const c = getAudioContext();
      if (!gainA.current) {
        gainA.current = c.createGain();
        gainB.current = c.createGain();
        gainA.current.gain.value = 0;
        gainB.current.gain.value = 0;
        // masterGain üzerinden → AnalyserNode'a da gider
        gainA.current.connect(masterGain!);
        gainB.current.connect(masterGain!);
      }
      c.resume().then(() => setAudioReady(true));
    };
    window.addEventListener("click", resume, { once: true });
    window.addEventListener("keydown", resume, { once: true });
    return () => {
      window.removeEventListener("click", resume);
      window.removeEventListener("keydown", resume);
    };
  }, [setAudioReady]);

  // Era / city crossfade
  useEffect(() => {
    if (!FEATURES.music) return;
    if (!audioReady || !activeCity || !era) return;
    if (!gainA.current || !gainB.current) return;

    const c = getAudioContext();
    const key = `${activeCity}/${era}`;
    if (key === loadedKey.current) return;
    loadedKey.current = key;

    fetch(`/cities/${activeCity}/music/${era}.mp3`)
      .then((r) => { if (!r.ok) throw new Error("404"); return r.arrayBuffer(); })
      .then((buf) => c.decodeAudioData(buf))
      .then((decoded) => {
        if (loadedKey.current !== key) return;

        const next = activeSlot.current === "a" ? "b" : "a";
        const outGain = next === "b" ? gainA.current! : gainB.current!;
        const inGain  = next === "b" ? gainB.current! : gainA.current!;
        const outSrc  = next === "b" ? sourceA.current : sourceB.current;

        const now = c.currentTime;
        outGain.gain.setValueAtTime(outGain.gain.value, now);
        outGain.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
        if (outSrc) try { outSrc.stop(now + FADE_DURATION + 0.1); } catch (_) {}

        const src = c.createBufferSource();
        src.buffer = decoded;
        src.loop = true;
        src.connect(inGain);
        inGain.gain.setValueAtTime(0, now);
        inGain.gain.linearRampToValueAtTime(VOLUME, now + FADE_DURATION);
        src.start(now);

        if (next === "b") sourceB.current = src;
        else sourceA.current = src;
        activeSlot.current = next;
      })
      .catch(() => {});
  }, [era, activeCity, audioReady]);

  // Şehir çıkınca fade-out
  useEffect(() => {
    if (!FEATURES.music) return;
    if (activeCity) return;
    const c = getAudioContext();
    const now = c.currentTime;
    gainA.current?.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
    gainB.current?.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
    loadedKey.current = "";
  }, [activeCity]);
}
