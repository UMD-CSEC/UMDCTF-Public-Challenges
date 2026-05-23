export type Side = "YES" | "NO";
export type Tier = "BRONZE" | "GOLD" | "DIAMOND";

export const SIDE_LABEL: Record<Side, string> = {
  YES: "YES",
  NO: "NO",
};

export const SIDE_COLOR: Record<Side, string> = {
  YES: "text-emerald-400",
  NO: "text-rose-400",
};

export const SIDE_BG: Record<Side, string> = {
  YES: "bg-emerald-500/10 border-emerald-500/40",
  NO: "bg-rose-500/10 border-rose-500/40",
};

export const TIER_LABEL: Record<Tier, string> = {
  BRONZE: "Bronze",
  GOLD: "Gold",
  DIAMOND: "Diamond",
};

export const TIER_COLOR: Record<Tier, string> = {
  BRONZE: "text-bronze",
  GOLD: "text-gold",
  DIAMOND: "text-diamond",
};

export const TIER_RING: Record<Tier, string> = {
  BRONZE: "ring-bronze/40",
  GOLD: "ring-gold/50",
  DIAMOND: "ring-diamond/60",
};

export function asSide(x: unknown): Side {
  return x === "YES" ? "YES" : "NO";
}

export function asTier(x: unknown): Tier {
  if (x === "DIAMOND" || x === "GOLD" || x === "BRONZE") return x;
  return "BRONZE";
}

export function formatCents(n: number) {
  return `${n}¢`;
}

export function formatRoi(n: number | string | { toString(): string }) {
  const s = typeof n === "string" ? n : n.toString();
  const v = Number(s);
  return `${v >= 0 ? "+" : ""}${v.toLocaleString("en-US", { maximumFractionDigits: 0 })}%`;
}
