/**
 * Module-level Audio singleton — tüm hooklar aynı context'i paylaşır.
 * Birden fazla AudioContext açmak bazı tarayıcılarda uyarı verir.
 */

export let ctx: AudioContext | null = null;
export let analyser: AnalyserNode | null = null;
export let masterGain: GainNode | null = null;

export function getAudioContext(): AudioContext {
  if (ctx) return ctx;

  ctx = new AudioContext();
  masterGain = ctx.createGain();
  masterGain.gain.value = 1;

  analyser = ctx.createAnalyser();
  analyser.fftSize = 128;           // 64 bin → yeterli çözünürlük, hafif
  analyser.smoothingTimeConstant = 0.82;

  masterGain.connect(analyser);
  analyser.connect(ctx.destination);

  return ctx;
}
