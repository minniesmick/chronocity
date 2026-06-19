import type { EraId } from "@/types";

export interface EraColor {
  hex: string;
  label: string;
  yearStart: number;
  yearEnd: number;
}

// Bina dönem renkleriyle tam eşleşir (buildingColors.ts ERA_BANDS ile senkron)
export const ERA_COLORS: EraColor[] = [
  { hex: "#b4966e", label: "Taş & Barok",  yearStart: 1800, yearEnd: 1870 },
  { hex: "#be7850", label: "Gründerzeit",  yearStart: 1870, yearEnd: 1918 },
  { hex: "#c8a53c", label: "Art Deco",     yearStart: 1918, yearEnd: 1945 },
  { hex: "#8c96a0", label: "Brutalizm",    yearStart: 1945, yearEnd: 1970 },
  { hex: "#afaf9b", label: "Prefab",       yearStart: 1970, yearEnd: 1990 },
  { hex: "#82af96", label: "Cam & Çelik",  yearStart: 1990, yearEnd: 2010 },
  { hex: "#64aad7", label: "Modern",       yearStart: 2010, yearEnd: 2100 },
];

export const ERA_UNKNOWN: EraColor = {
  hex: "#64748b", label: "Tarihi Belirsiz", yearStart: 0, yearEnd: 0,
};

/** Yıla göre era rengi + label — null → ERA_UNKNOWN */
export function eraByYear(year: number | null): EraColor {
  if (!year) return ERA_UNKNOWN;
  return (
    ERA_COLORS.find((e) => year >= e.yearStart && year < e.yearEnd) ??
    ERA_COLORS[ERA_COLORS.length - 1]
  );
}

/** Müzik EraId → building era rengi (dönem eşleşmesi) */
export const ERA_ID_COLORS: Record<EraId, EraColor> = {
  "1960s":  ERA_COLORS[3], // Brutalizm
  "1980s":  ERA_COLORS[4], // Prefab
  "2000s":  ERA_COLORS[5], // Cam & Çelik
  modern:   ERA_COLORS[6], // Modern
};
